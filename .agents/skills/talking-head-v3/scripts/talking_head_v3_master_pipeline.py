#!/usr/bin/env python3
"""Plan Split B-Roll, generate the audio graph, and check 9:16 captions."""

import argparse
from fnmatch import fnmatchcase
import json
import math
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile


FPS = 30
SCENE_COUNT = 4
MIN_SCENE_FRAMES = 12
TARGET_SCENE_FRAMES = 72
CANVAS = {"width": 1080, "height": 1920, "fps": FPS}
CAPTION_BOUNDS = (54, 248, 884, 1545)
TRACK_BOXES = {"flow": [86, 270, 852, 735], "showcase": [86, 768, 852, 1233]}


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} phải là số hữu hạn")
    return value


def time_range(entry, label):
    if not isinstance(entry, dict):
        raise ValueError(f"{label} phải là object")
    start = number(entry.get("start"), f"{label}.start")
    end = number(entry.get("end"), f"{label}.end")
    if not 0 <= start < end:
        raise ValueError(f"{label} cần 0 <= start < end")
    return start, end


def transcript_intervals(data):
    entries = data.get("segments", data.get("words")) if isinstance(data, dict) else data
    if not isinstance(entries, list) or not entries:
        raise ValueError("Transcript cần danh sách segments hoặc words có mốc start/end")
    intervals = []
    timeline_end = 0
    for entry in entries:
        start, end = time_range(entry, "Đoạn thoại")
        timeline_end = max(timeline_end, end)
        words = entry.get("words", [])
        if not isinstance(words, list):
            raise ValueError("segments[].words phải là danh sách")
        for word in words or [entry]:
            ws, we = time_range(word, "Từ thoại") if words else (start, end)
            content = word.get("word", word.get("text", ""))
            if isinstance(content, str) and content.strip():
                intervals.append((ws, we, content.strip()))
    if not intervals:
        raise ValueError("Transcript cần ít nhất một đoạn thoại có nội dung")
    return sorted(intervals), max(timeline_end, max(end for _, end, _ in intervals))


def scene_slots(frame_count, protected_ranges):
    """Partition available footage while leaving protected A-Roll intact."""
    protected = sorted(time_range(entry, "protected_ranges[]") for entry in protected_ranges)
    free = []
    cursor = 0
    for start, end in protected:
        first = min(frame_count, math.floor(start * FPS + 1e-8))
        if first - cursor >= MIN_SCENE_FRAMES:
            free.append((cursor, first))
        cursor = max(cursor, min(frame_count, math.ceil(end * FPS - 1e-8)))
    if frame_count - cursor >= MIN_SCENE_FRAMES:
        free.append((cursor, frame_count))

    while len(free) < SCENE_COUNT:
        if not free:
            raise ValueError("Timeline còn quá ít A-Roll khả dụng để xếp 4 cảnh Split B-Roll")
        start, end = max(free, key=lambda slot: slot[1] - slot[0])
        if end - start < 2 * MIN_SCENE_FRAMES:
            raise ValueError("Cần đủ chỗ cho 4 cảnh, mỗi cảnh ít nhất 12 frame")
        left_count = ((end - start) // MIN_SCENE_FRAMES) // 2
        midpoint = min(end - MIN_SCENE_FRAMES, start + left_count * MIN_SCENE_FRAMES)
        free.remove((start, end))
        free.extend([(start, midpoint), (midpoint, end)])

    return sorted(sorted(free, key=lambda slot: slot[1] - slot[0], reverse=True)[:SCENE_COUNT])


def media_layer(assets, track, index):
    is_flow = track == "flow"
    source_key = "flow_src" if is_flow else "product_src"
    focus_key = "flow_focus" if is_flow else "product_focus"
    default_source = f"assets/flow_{index:02}.mp4" if is_flow else "assets/SP_PRODUCT_CUTOUT.png"
    source = assets.get(source_key, default_source)
    if not isinstance(source, str) or not source.strip():
        raise ValueError(f"assets[{index - 1}].{source_key} cần đường dẫn media")
    filename = source.replace("\\", "/").rsplit("/", 1)[-1]
    if not is_flow and not fnmatchcase(filename, "SP_?*_CUTOUT.png"):
        raise ValueError(f"assets[{index - 1}].product_src cần tên SP_*_CUTOUT.png")
    focus = assets.get(focus_key, [0.5, 0.5])
    if (not isinstance(focus, list) or len(focus) != 2
            or any(not 0 <= number(v, focus_key) <= 1 for v in focus)):
        raise ValueError(f"{focus_key} cần [x, y] trong [0, 1]")
    in_seconds = number(assets.get("flow_in", 0), "flow_in") if is_flow else 0
    if in_seconds < 0:
        raise ValueError("flow_in phải >= 0")
    return {
        "track": track,
        "media_type": "video" if is_flow else "image",
        "src": source,
        "source_start": in_seconds,
        "bbox": TRACK_BOXES[track],
        "fit": "fit-cover",
        "focus": focus,
        "aspect_ratio_locked": True,
        "distortion_percent": 0,
    }


def plan_split_broll(transcript):
    intervals, spoken_end = transcript_intervals(transcript)
    options = transcript if isinstance(transcript, dict) else {}
    duration = number(options.get("duration", spoken_end), "duration")
    if duration <= 0 or spoken_end > duration + 1e-8:
        raise ValueError("duration phải bao hết các mốc thoại")
    frame_count = math.ceil(duration * FPS - 1e-8)
    protected = options.get("protected_ranges", [])
    assets = options.get("assets", [{} for _ in range(SCENE_COUNT)])
    if not isinstance(protected, list):
        raise ValueError("protected_ranges phải là danh sách")
    if (not isinstance(assets, list) or len(assets) != SCENE_COUNT
            or any(not isinstance(entry, dict) for entry in assets)):
        raise ValueError("assets phải chứa 4 object theo thứ tự cảnh")

    boundaries = [round(start * FPS) for start, _, _ in intervals]
    scenes = []
    for index, (slot_start, slot_end) in enumerate(scene_slots(frame_count, protected), 1):
        length = max(MIN_SCENE_FRAMES, min(TARGET_SCENE_FRAMES, (slot_end - slot_start) * 3 // 5))
        ideal = (slot_start + slot_end - length) // 2
        nearby = [frame for frame in boundaries
                  if slot_start <= frame <= slot_end - length and abs(frame - ideal) <= 18]
        start = min(nearby, key=lambda frame: abs(frame - ideal), default=ideal)
        end = start + length
        speech = [content for ws, we, content in intervals if ws < end / FPS and we > start / FPS]
        if not speech:
            anchors = [max(slot_start, min(math.floor(ws * FPS), slot_end - length))
                       for ws, we, _ in intervals if ws < slot_end / FPS and we > slot_start / FPS]
            if anchors:
                start = min(anchors, key=lambda frame: abs(frame - ideal))
                end = start + length
                speech = [content for ws, we, content in intervals if ws < end / FPS and we > start / FPS]
        fade = min(15, length // 3)
        scenes.append({
            "id": f"split_{index:02}",
            "start_frame": start,
            "end_frame": end,
            "start": round(start / FPS, 6),
            "end": round(end / FPS, 6),
            "narration": " ".join(speech),
            "transition_frames": min(13, length // 3),
            "dim_room_alpha": [
                {"frame": start, "alpha": 0.0},
                {"frame": start + fade, "alpha": 0.42},
                {"frame": end - fade, "alpha": 0.42},
                {"frame": end, "alpha": 0.0},
            ],
            "dim_easing": "smoothstep",
            "layers": [media_layer(assets[index - 1], track, index) for track in TRACK_BOXES],
        })
    return {"canvas": CANVAS, "duration_frames": frame_count, "scenes": scenes}


def build_audio_filtergraph(duration=60, split_at=None, stats=None):
    """Use VO, warm C-major BGM and bright C-major BGM, in that input order."""
    duration = number(duration, "duration")
    midpoint = duration / 2 if split_at is None else number(split_at, "split_at")
    if duration < 0.1 or not 0 < midpoint < duration or min(midpoint, duration - midpoint) < 0.001:
        raise ValueError("Cần duration >= 0.1s và split_at nằm trong thời lượng")
    crossfade = min(1.6, midpoint, duration - midpoint)
    warm_end = midpoint + crossfade / 2
    bright_length = duration - midpoint + crossfade / 2
    duration_text = f"{duration:.6f}"
    audio_format = "aresample=48000,aformat=channel_layouts=stereo"
    final_norm = "loudnorm=I=-14.0:TP=-0.95:LRA=11:print_format=json"
    if stats is not None:
        if not isinstance(stats, dict):
            raise ValueError("loudnorm stats phải là JSON object từ lượt đo đầu")
        values = {
            "measured_I": ("input_i", -99, 0), "measured_TP": ("input_tp", -99, 99),
            "measured_LRA": ("input_lra", 0, 99), "measured_thresh": ("input_thresh", -99, 0),
            "offset": ("target_offset", -99, 99),
        }
        for option, (key, low, high) in values.items():
            try:
                value = float(stats[key])
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Thiếu hoặc sai giá trị loudnorm {key}") from error
            if not low <= value <= high:
                raise ValueError(f"Giá trị loudnorm {key} nằm ngoài miền hợp lệ")
            final_norm += f":{option}={value:.6f}"
        final_norm += ":linear=true"

    bgm_norm = f"loudnorm=I=-17:TP=-1.5:LRA=11,{audio_format}"
    fade_out = min(2.2, bright_length / 3)
    return ";\n".join([
        f"[0:a]asetpts=PTS-STARTPTS,{audio_format},highpass=f=80,apad=whole_dur={duration_text},"
        f"atrim=duration={duration_text},asplit=2[voice][voice_sc]",
        f"[1:a]atrim=duration={warm_end:.6f},asetpts=PTS-STARTPTS,{bgm_norm},"
        f"afade=t=in:d={min(1.0, warm_end / 3):.6f}[warm]",
        f"[2:a]atrim=duration={bright_length:.6f},asetpts=PTS-STARTPTS,{bgm_norm},"
        f"afade=t=out:st={bright_length - fade_out:.6f}:d={fade_out:.6f}[bright]",
        f"[warm][bright]acrossfade=d={crossfade:.6f}:c1=tri:c2=tri,"
        "highpass=f=75,equalizer=f=1850:t=q:w=1.4:g=-3.5,volume=-11dB[bgm_eq]",
        "[bgm_eq][voice_sc]sidechaincompress=threshold=0.025:ratio=3.2:attack=35:release=380[ducked]",
        f"[voice][ducked]amix=inputs=2:duration=first:normalize=0,{final_norm},{audio_format}[aout]",
    ])


def caption_box(word):
    raw = word.get("bbox", word)
    if isinstance(raw, (list, tuple)) and len(raw) == 4:
        left, top, right, bottom = (number(v, "bbox") for v in raw)
    elif isinstance(raw, dict) and "left" in raw:
        left, top, right, bottom = (number(raw.get(key), key) for key in ("left", "top", "right", "bottom"))
    elif isinstance(raw, dict) and "x" in raw:
        left, top, width, height = (number(raw.get(key), key) for key in ("x", "y", "width", "height"))
        right, bottom = left + width, top + height
    else:
        raise ValueError("Cần bbox [left, top, right, bottom] hoặc x/y/width/height theo px")
    if not left < right or not top < bottom:
        raise ValueError("bbox phải có chiều rộng và chiều cao dương")
    glow = number(word.get("glow_padding", 0), "glow_padding")
    if glow < 0:
        raise ValueError("glow_padding phải >= 0")
    return left - glow, top - glow, right + glow, bottom + glow


def check_subtitles(data):
    words = data.get("words") if isinstance(data, dict) else data
    if not isinstance(words, list) or not words:
        raise ValueError("Cần danh sách từ có bbox để kiểm vùng an toàn")
    violations = []
    min_x, min_y, max_x, max_y = CAPTION_BOUNDS
    for index, word in enumerate(words):
        if not isinstance(word, dict):
            violations.append({"index": index, "error": "Mỗi từ phải là object"})
            continue
        label = {"index": index, "word": word.get("word", word.get("text", ""))}
        try:
            left, top, right, bottom = caption_box(word)
        except ValueError as error:
            violations.append({**label, "error": str(error)})
            continue
        zones = []
        if top < min_y:
            zones.append("top")
        if bottom > max_y:
            zones.append("bottom")
        if left < min_x:
            zones.append("left")
        if right > 1024 and top < 860:
            zones.append("top_right")
        if right > max_x and bottom > 860 and top < 1548:
            zones.append("interaction_right")
        if right > max_x and not {"top_right", "interaction_right"}.intersection(zones):
            zones.append("subtitle_right")
        if zones:
            violations.append({**label, "bbox": [left, top, right, bottom], "zones": zones})
    return {"ok": not violations, "checked_words": len(words), "violations": violations}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def write_output(path, content):
    if path is None:
        print(content)
        return
    with NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(content + "\n")
            handle.close()
            temporary.replace(path)
        finally:
            if not handle.closed:
                handle.close()
            temporary.unlink(missing_ok=True)


def self_test():
    segments = [{"start": n, "end": n + 0.75, "words": [
        {"word": " Dược sĩ", "start": n, "end": n + 0.75}
    ]} for n in range(20)]
    assets = [{"flow_focus": [0.3, 0.7], "flow_in": 0.2, "product_src": "assets/SP_LT_PLUS_CUTOUT.png"}] * 4
    payload = {"segments": segments, "duration": 20, "assets": assets,
               "protected_ranges": [{"start": 8, "end": 12}]}
    plan = plan_split_broll(payload)
    scenes = plan["scenes"]
    assert len(scenes) == 4 and plan["duration_frames"] == 600
    assert all(a["end_frame"] <= b["start_frame"] for a, b in zip(scenes, scenes[1:]))
    for scene in scenes:
        start, end = scene["start_frame"], scene["end_frame"]
        assert 0 <= start < end <= 600 and (end <= 240 or start >= 360)
        assert "Dược sĩ" in scene["narration"]
        assert [cue["alpha"] for cue in scene["dim_room_alpha"]] == [0.0, 0.42, 0.42, 0.0]
        assert [cue["frame"] for cue in scene["dim_room_alpha"]] == [start, start + 15, end - 15, end]
        flow, showcase = scene["layers"]
        assert flow["media_type"] == "video" and flow["source_start"] == 0.2
        assert flow["focus"] == [0.3, 0.7] and showcase["src"].endswith("SP_LT_PLUS_CUTOUT.png")
        assert all(layer["fit"] == "fit-cover" and layer["distortion_percent"] == 0 for layer in scene["layers"])

    assert json.loads(json_text(plan)) == plan and "Dược sĩ" in json_text(plan)

    short = plan_split_broll([{"start": 0, "end": 1.6, "word": "Một đoạn ngắn"}])
    assert all(scene["end_frame"] - scene["start_frame"] == 12 for scene in short["scenes"])
    graph = build_audio_filtergraph(60, 25)
    assert "atrim=duration=25.800000" in graph and "atrim=duration=35.800000" in graph
    assert "equalizer=f=1850:t=q:w=1.4:g=-3.5" in graph and "[bgm_eq][voice_sc]sidechaincompress" in graph
    assert "loudnorm=I=-14.0:TP=-0.95" in graph and graph.endswith("[aout]")
    measured = {"input_i": "-16.4", "input_tp": "-2", "input_lra": "3", "input_thresh": "-27", "target_offset": "0.10"}
    assert "measured_I=-16.400000" in build_audio_filtergraph(stats=measured)
    assert "linear=true" in build_audio_filtergraph(stats=measured)
    assert "acrossfade=d=0.250000" in build_audio_filtergraph(0.5)

    safe = {"word": "Sáng", "bbox": [54, 248, 884, 1545]}
    assert check_subtitles([safe])["ok"]
    cases = [safe, {"bbox": [50, 245, 1030, 1546]}, {"bbox": [85, 700, 884, 800], "glow_padding": 2},
             {"bbox": {"x": 100, "y": 900, "width": 785, "height": 100}}, {"word": "thiếu bbox"}]
    report = check_subtitles({"words": cases})
    assert not report["ok"] and report["checked_words"] == 5
    assert set(report["violations"][0]["zones"]) == {"top", "bottom", "left", "top_right", "interaction_right"}
    assert report["violations"][1]["zones"] == ["subtitle_right"]
    assert report["violations"][2]["zones"] == ["interaction_right"] and "error" in report["violations"][3]
    for operation in (lambda: plan_split_broll([{"start": 0, "end": 1, "word": "Ngắn"}]),
                      lambda: build_audio_filtergraph(stats={**measured, "input_i": "-inf"}),
                      lambda: check_subtitles([])):
        try:
            operation()
        except ValueError:
            continue
        raise AssertionError("Dữ liệu không hợp lệ đã được chấp nhận")
    print("SELF_TEST_OK")


def main():
    parser = argparse.ArgumentParser(description="Talking Head V3 · Bộ công cụ V6 Siêu Cấp")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--plan-split-broll", type=Path, metavar="TRANSCRIPT_JSON")
    modes.add_argument("--build-audio-filtergraph", action="store_true")
    modes.add_argument("--check-subtitles", type=Path, metavar="WORDS_JSON")
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path, help="Tệp UTF-8 cho plan hoặc filtergraph")
    parser.add_argument("--duration", type=float, help="Thời lượng phối âm, mặc định 60 giây")
    parser.add_argument("--split-at", type=float, help="Tâm crossfade, mặc định giữa thời lượng")
    parser.add_argument("--loudnorm-stats", type=Path, help="JSON loudnorm từ lượt đo đầu")
    args = parser.parse_args()

    if args.plan_split_broll and args.out is None:
        parser.error("--plan-split-broll cần --out")
    if args.out and not (args.plan_split_broll or args.build_audio_filtergraph):
        parser.error("--out dành cho plan hoặc filtergraph")
    if not args.build_audio_filtergraph and any(v is not None for v in (args.duration, args.split_at, args.loudnorm_stats)):
        parser.error("Tùy chọn phối âm cần --build-audio-filtergraph")
    try:
        source = args.plan_split_broll or args.loudnorm_stats
        if args.out and source and args.out.resolve() == source.resolve():
            raise ValueError("Đường dẫn --out phải khác tệp đầu vào")
        if args.self_test:
            self_test()
        elif args.plan_split_broll:
            write_output(args.out, json_text(plan_split_broll(read_json(args.plan_split_broll))))
        elif args.build_audio_filtergraph:
            stats = read_json(args.loudnorm_stats) if args.loudnorm_stats else None
            if args.loudnorm_stats and not isinstance(stats, dict):
                raise ValueError("loudnorm stats phải là JSON object từ lượt đo đầu")
            duration = 60 if args.duration is None else args.duration
            write_output(args.out, build_audio_filtergraph(duration, args.split_at, stats))
        else:
            report = check_subtitles(read_json(args.check_subtitles))
            print(json_text(report))
            return 0 if report["ok"] else 1
    except (OSError, ValueError, OverflowError) as error:
        parser.exit(2, f"Lỗi: {error}\n")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
