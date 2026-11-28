#!/usr/bin/env python3
"""Build a frame-aligned Full Studio audio mix with FFmpeg."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PureWindowsPath


SAMPLE_RATE = 48_000
VOICE_LUFS = -14.5
SFX_OFFSET_DB = -11.0
BGM_OFFSET_DB = -14.5
WHOOSH_LEAD = SAMPLE_RATE * 110 // 1000
AUTO_SEQUENCE_GAP = SAMPLE_RATE // 2
FORBIDDEN_FILE = "Whoosh - Lướt chuyển cảnh cơ bản.mp3"
BUNDLED_SFX = Path(__file__).resolve().parents[1] / "audio" / "assets" / "sfx"
EFFECT_FILES = {
    "pop": "pop.mp3",
    "click": "click.mp3",
    "card_riffle": None,
    "soft_ping": "ping.mp3",
    "airy_whoosh": "whoosh-short.mp3",
}


@dataclass
class Cue:
    effect: str
    path: Path
    target_sample: int
    source_onset: int
    sequence_id: str | None
    semitones: int = 0

    @property
    def start_sample(self) -> int:
        if self.effect == "airy_whoosh":
            return self.target_sample - WHOOSH_LEAD
        return self.target_sample


@dataclass
class MixSpec:
    voice: Path
    bgm: Path | None
    existing_bgm_detected: bool
    events: list[Cue]

    @property
    def active_bgm(self) -> Path | None:
        return None if self.existing_bgm_detected else self.bgm


def check_filename(path: str) -> None:
    filename = PureWindowsPath(path).name.rstrip(" .")
    if unicodedata.normalize("NFC", filename).casefold() == FORBIDDEN_FILE.casefold():
        raise ValueError(f"Tệp âm thanh bị cấm: {FORBIDDEN_FILE}")


def audio_path(value: object, base: Path, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} phải là đường dẫn tệp âm thanh")
    check_filename(value)
    path = (base / Path(value).expanduser()).resolve()
    check_filename(str(path))
    return path


def milliseconds_to_samples(value: object, field: str) -> int:
    if type(value) not in (int, float) or value < 0:
        raise ValueError(f"{field} phải là số mili giây hữu hạn, không âm")
    try:
        return round(Fraction(str(value)) * SAMPLE_RATE / 1000)
    except ValueError as exc:
        raise ValueError(f"{field} phải là số mili giây hữu hạn, không âm") from exc


def pitch_sequence(events: list[Cue]) -> None:
    if 3 <= len(events) <= 5:
        for step, event in enumerate(events):
            event.semitones = step


def assign_pitch(events: list[Cue]) -> None:
    tagged = defaultdict(list)
    run: list[Cue] = []
    for event in events:
        if event.sequence_id is not None:
            tagged[event.sequence_id].append(event)
            pitch_sequence(run)
            run.clear()
            continue
        if event.effect == "airy_whoosh":
            continue
        if run and not 0 < event.target_sample - run[-1].target_sample <= AUTO_SEQUENCE_GAP:
            pitch_sequence(run)
            run.clear()
        run.append(event)
    pitch_sequence(run)

    for sequence_id, group in tagged.items():
        if not 3 <= len(group) <= 5 or len({cue.target_sample for cue in group}) != len(group):
            raise ValueError(f"sequence_id {sequence_id!r} cần 3–5 mốc thời gian khác nhau")
        pitch_sequence(group)


def parse_spec(data: object, base: Path) -> MixSpec:
    if not isinstance(data, dict):
        raise ValueError("Mix spec phải là một JSON object")
    voice = audio_path(data.get("voice"), base, "voice")
    bgm = data.get("bgm")
    bgm = audio_path(bgm, base, "bgm") if bgm is not None else None
    existing_bgm = data.get("existing_bgm_detected", False)
    if type(existing_bgm) is not bool:
        raise ValueError("existing_bgm_detected phải là true hoặc false")

    fps = None
    if "fps" in data:
        try:
            fps = Fraction(str(data["fps"]))
            if fps <= 0:
                raise ValueError
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError('fps phải dương, ví dụ 30 hoặc "30000/1001"') from exc

    events = data.get("events", [])
    if not isinstance(events, list):
        raise ValueError("events phải là một danh sách")
    cues = []
    for index, event in enumerate(events):
        field = f"events[{index}]"
        if not isinstance(event, dict):
            raise ValueError(f"{field} phải là một JSON object")
        effect = event.get("type")
        if effect == "whoosh":
            effect = "airy_whoosh"
        if not isinstance(effect, str) or effect not in EFFECT_FILES:
            raise ValueError(f"{field}.type phải là một trong {', '.join(EFFECT_FILES)}")
        bundled_file = EFFECT_FILES[effect]
        default_path = str(BUNDLED_SFX / bundled_file) if bundled_file else None
        path = audio_path(event.get("path", default_path), base, f"{field}.path")

        if ("frame" in event) == ("time_ms" in event):
            raise ValueError(f"{field} cần đúng một trường frame hoặc time_ms")
        if "frame" in event:
            frame = event["frame"]
            if fps is None or type(frame) is not int or frame < 0:
                raise ValueError(f"{field}.frame cần số nguyên không âm và fps trong mix spec")
            target = round(frame * SAMPLE_RATE / fps)
        else:
            target = milliseconds_to_samples(event["time_ms"], f"{field}.time_ms")

        onset = milliseconds_to_samples(event.get("source_onset_ms", 0), f"{field}.source_onset_ms")
        sequence = event.get("sequence_id")
        if sequence is not None and (not isinstance(sequence, str) or not sequence.strip()):
            raise ValueError(f"{field}.sequence_id phải là chuỗi có nội dung")
        cues.append(Cue(effect, path, target, onset, sequence))

    cues.sort(key=lambda cue: cue.target_sample)
    assign_pitch(cues)
    return MixSpec(voice, bgm, existing_bgm, cues)


def prepare_streams(spec: MixSpec) -> tuple[list[Path], list[str]]:
    bgm = spec.active_bgm
    sources = [spec.voice, *(cue.path for cue in spec.events)]
    if bgm is not None:
        sources.append(bgm)
    inputs = list(dict.fromkeys(sources))
    indexes = {path: index for index, path in enumerate(inputs)}
    stereo = f"aresample={SAMPLE_RATE},aformat=sample_fmts=fltp:channel_layouts=stereo"
    reset = "asetpts=N/SR/TB"
    voice_norm = f"loudnorm=I={VOICE_LUFS}:TP=-1.5:LRA=11:print_format=json"
    streams = [f"[{indexes[spec.voice]}:a:0]{stereo},{reset},{voice_norm},{stereo},{reset}"]

    for cue in spec.events:
        filters = [stereo]
        if cue.source_onset:
            filters.append(f"atrim=start_sample={cue.source_onset}")
        if cue.semitones:
            pitch_rate = round(SAMPLE_RATE * 2 ** (cue.semitones / 12))
            filters.extend((f"asetrate={pitch_rate}", f"aresample={SAMPLE_RATE}"))
        if cue.start_sample < 0:
            filters.append(f"atrim=start_sample={-cue.start_sample}")
        filters.append(reset)
        streams.append(f"[{indexes[cue.path]}:a:0]" + ",".join(filters))

    if bgm is not None:
        streams.append(f"[{indexes[bgm]}:a:0]{stereo},{reset}")
    return inputs, streams


def build_filtergraph(spec: MixSpec, streams: list[str], gains: list[float]) -> str:
    filters = [f"{streams[0]},volume={gains[0]:.6f}dB[voice]"]
    foreground = ["[voice]"]
    for index, cue in enumerate(spec.events, start=1):
        start = max(0, cue.start_sample)
        label = f"[sfx{index}]"
        filters.append(f"{streams[index]},volume={gains[index]:.6f}dB,adelay={start}S:all=1{label}")
        foreground.append(label)

    master = "[foreground]"
    filters.append(
        "".join(foreground) + f"amix=inputs={len(foreground)}:duration=longest:normalize=0{master}"
    )
    if spec.active_bgm is not None:
        filters.append(f"{streams[-1]},volume={gains[-1]:.6f}dB[bgm]")
        filters.append(f"{master}[bgm]amix=inputs=2:duration=first:normalize=0[master]")
        master = "[master]"
    filters.append(f"{master}alimiter=limit=0.89125094:level=false:latency=true[mix]")
    return ";\n".join(filters)


def run_ffmpeg(command: list[str], arguments: list[str]) -> str:
    result = subprocess.run(
        command + arguments, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        detail = "\n".join(result.stderr.strip().splitlines()[-12:])
        raise ValueError(f"FFmpeg lỗi ({result.returncode})\n{detail}")
    return result.stderr


def measure_gains(command: list[str], streams: list[str], nominal_gains: list[float]) -> list[float]:
    meters = []
    outputs = []
    for index, stream in enumerate(streams):
        label = f"[rms{index}]"
        meters.append(f"{stream},astats@rms{index}=measure_perchannel=none:measure_overall=RMS_level{label}")
        outputs.extend(("-map", label))

    log = run_ffmpeg(command, ["-filter_complex", ";\n".join(meters), *outputs, "-f", "null", "-"])
    rms = {
        int(index): float(level) for index, level in re.findall(
            r"\[astats@rms(\d+)\s+@\s+[^\]]+\]\s+RMS level dB:\s*(\S+)", log
        )
    }
    if len(rms) != len(streams):
        raise ValueError("FFmpeg không trả đủ kết quả đo RMS cho các nguồn âm thanh")
    integrated = re.search(r'"output_i"\s*:\s*"([^"]+)"', log)
    if integrated is None or not math.isfinite(rms[0]):
        raise ValueError("Không đo được thoại. Kiểm tra nguồn voice có tín hiệu âm thanh")
    voice_lufs = float(integrated.group(1))
    if not math.isfinite(voice_lufs):
        raise ValueError("Thoại quá ngắn hoặc quá nhỏ để đo LUFS tích hợp")

    voice_gain = VOICE_LUFS - voice_lufs
    voice_rms = rms[0] + voice_gain
    gains = [voice_gain]
    for index, offset in enumerate(nominal_gains[1:], start=1):
        gains.append(voice_rms + offset - rms[index] if math.isfinite(rms[index]) else 0.0)
    return gains


def render_mix(
    spec: MixSpec, inputs: list[Path], streams: list[str], nominal_gains: list[float], output: Path,
) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ValueError("Cần FFmpeg trong PATH để xuất WAV")
    for path in inputs:
        if not path.is_file():
            raise ValueError(f"Không tìm thấy nguồn âm thanh: {path}")
    command = [ffmpeg, "-hide_banner", "-nostdin", "-nostats"]
    for path in inputs:
        command.extend(("-i", str(path)))

    gains = measure_gains(command, streams, nominal_gains)
    graph = build_filtergraph(spec, streams, gains)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix="studio_mix_") as workdir:
        temporary_output = Path(workdir) / "mix.wav"
        run_ffmpeg(command, ["-filter_complex", graph, "-map", "[mix]", "-c:a", "pcm_s24le", str(temporary_output)])
        temporary_output.replace(output)


def nominal_gains(spec: MixSpec) -> list[float]:
    gains = [0.0, *([SFX_OFFSET_DB] * len(spec.events))]
    if spec.active_bgm is not None:
        gains.append(BGM_OFFSET_DB)
    return gains


def self_test() -> None:
    root = Path(__file__).resolve().parent
    data = {
        "voice": "voice.wav", "bgm": "bgm.wav", "fps": "30000/1001",
        "events": [
            {"type": "card_riffle", "path": "cards.wav", "frame": 24},
            {"type": "airy_whoosh", "time_ms": 40},
            {"type": "pop", "frame": 12, "source_onset_ms": 10},
            {"type": "click", "frame": 18},
            {"type": "airy_whoosh", "time_ms": 900},
            {"type": "soft_ping", "time_ms": 1300},
        ],
    }
    spec = parse_spec(data, root)
    _, streams = prepare_streams(spec)
    graph = build_filtergraph(spec, streams, nominal_gains(spec))
    assert [cue.semitones for cue in spec.events] == [0, 0, 1, 2, 0, 3]
    assert "atrim=start_sample=3360,asetpts=N/SR/TB,volume=-11.000000dB,adelay=0S" in graph
    assert "atrim=start_sample=480,asetpts=N/SR/TB,volume=-11.000000dB,adelay=19219S" in graph
    assert "asetrate=50854,aresample=48000,asetpts=N/SR/TB,volume=-11.000000dB,adelay=28829S" in graph
    assert "adelay=37920S:all=1" in graph
    assert "loudnorm=I=-14.5" in graph and "volume=-14.500000dB[bgm]" in graph
    assert "duration=first:normalize=0" in graph and graph.endswith("[mix]")

    muted = parse_spec({**data, "existing_bgm_detected": True}, root)
    inputs, streams = prepare_streams(muted)
    assert root / "bgm.wav" not in inputs
    assert "[bgm]" not in build_filtergraph(muted, streams, nominal_gains(muted))

    tagged = parse_spec({"voice": "voice.wav", "events": [
        {"type": "pop", "time_ms": time, "sequence_id": "cards"}
        for time in (4000, 0, 2000, 1000, 3000)
    ]}, root)
    assert [cue.semitones for cue in tagged.events] == [0, 1, 2, 3, 4]

    banned = unicodedata.normalize("NFD", FORBIDDEN_FILE.upper())
    for blocked in (
        {**data, "voice": FORBIDDEN_FILE},
        {**data, "bgm": f"assets/{banned}", "existing_bgm_detected": True},
        {**data, "events": [{"type": "whoosh", "time_ms": 200, "path": f"assets\\{banned}"}]},
    ):
        try:
            parse_spec(blocked, root)
        except ValueError as exc:
            if FORBIDDEN_FILE in str(exc):
                continue
            raise
        raise AssertionError("Mix spec đã lọt tệp âm thanh bị cấm")
    print("SELF_TEST_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phối Voice, Tactile Micro-SFX và BGM chuẩn Full Studio V6.")
    parser.add_argument("--spec", type=Path, help="Mix spec JSON UTF-8")
    parser.add_argument("--out", type=Path, help="WAV stereo 48 kHz, PCM 24-bit")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run-filter", action="store_true", help="In filtergraph dự kiến, không chạy FFmpeg")
    modes.add_argument("--self-test", action="store_true", help="Kiểm thử filtergraph và chặn tệp cấm")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.spec is None or (args.out is None and not args.dry_run_filter):
        parser.error("cần --spec và --out khi xuất WAV. --dry-run-filter chỉ cần --spec")

    try:
        spec_path = args.spec.resolve()
        spec = parse_spec(json.loads(spec_path.read_text(encoding="utf-8-sig")), spec_path.parent)
        inputs, streams = prepare_streams(spec)
        gains = nominal_gains(spec)
        if args.dry_run_filter:
            for index, path in enumerate(inputs):
                print(f"Input {index}: {path}", file=sys.stderr)
            print(build_filtergraph(spec, streams, gains))
            return

        output = args.out.resolve()
        if output.suffix.lower() != ".wav":
            raise ValueError("--out cần đuôi .wav")
        if output in [spec_path, spec.bgm, *inputs]:
            raise ValueError("--out trùng với tệp nguồn")
        render_mix(spec, inputs, streams, gains, output)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"Lỗi: {exc}\n")


if __name__ == "__main__":
    main()
