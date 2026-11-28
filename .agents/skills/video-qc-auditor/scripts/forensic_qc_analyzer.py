#!/usr/bin/env python3
"""Quét kỹ thuật từng frame và xuất báo cáo JSON cho kiểm duyệt video V6."""

import argparse
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import groupby
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import cv2
import numpy as np


BLACK_MAX = 18
WHITE_MIN = 242
BLANK_FRACTION = 0.985
FLASH_MAX_S = 0.125
FLASH_MIN_LUMA_JUMP = 20
BAR_MIN_S = 0.25
BAR_MIN_PX = 2
BAR_TOLERANCE_PX = 2
SIDES = ("top", "bottom", "left", "right")
VERTICAL_SIZE = (1080, 1920)

# [x1, y1, x2, y2), theo mặt nạ audit_rgba_overlay_safe_zone.
ZONES = {
    "top": (0, 0, 1080, 250),
    "bottom": (0, 1545, 1080, 1920),
    "left": (0, 0, 54, 1920),
    "upper_right": (1024, 0, 1080, 860),
    "lower_right": (884, 860, 1080, 1545),
}


def run_tool(command: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"{command[0]} ({result.returncode}): {result.stderr.strip()[-2000:]}")
    return result


def as_fraction(value) -> Fraction | None:
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return None


def stream_duration(video: Path, stream: dict) -> float | None:
    time_base = as_fraction(stream.get("time_base"))
    duration_ticks = as_fraction(stream.get("duration_ts"))
    if time_base and duration_ticks and duration_ticks > 0:
        return float(time_base * duration_ticks)

    duration = as_fraction(stream.get("duration"))
    if duration and duration > 0:
        return float(duration)
    if not time_base:
        return None

    # Dùng dòng thời gian của riêng track khi metadata thiếu thời lượng.
    result = run_tool([
        "ffprobe", "-v", "error", "-select_streams", str(stream["index"]),
        "-show_packets", "-show_entries", "packet=pts,duration", "-of", "json", str(video),
    ])
    first_pts = last_pts = last_end = None
    for packet in json.loads(result.stdout).get("packets", []):
        pts = as_fraction(packet.get("pts"))
        length = as_fraction(packet.get("duration"))
        if pts is None:
            continue
        first_pts = pts if first_pts is None else min(first_pts, pts)
        last_pts = pts if last_pts is None else max(last_pts, pts)
        if length and length > 0:
            end = pts + length
            last_end = end if last_end is None else max(last_end, end)
    if last_end is None or last_end <= last_pts:
        return None
    return float((last_end - first_pts) * time_base)


def probe(video: Path) -> tuple[dict, dict | None, tuple[int, int]]:
    result = run_tool(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(video)])
    streams = json.loads(result.stdout).get("streams", [])
    picture = next((
        stream for stream in streams
        if stream["codec_type"] == "video" and not stream.get("disposition", {}).get("attached_pic")
    ), None)
    if picture is None:
        raise ValueError("Không tìm thấy track hình.")
    sound = next((stream for stream in streams if stream["codec_type"] == "audio"), None)
    width, height = picture["width"], picture["height"]
    if min(width, height) <= 0:
        raise ValueError("Track hình thiếu kích thước hợp lệ.")
    rotation = next(
        (side["rotation"] for side in picture.get("side_data_list", []) if "rotation" in side),
        0,
    )
    quarter_turns = round(rotation / 90)
    if abs(rotation - quarter_turns * 90) >= 1:
        raise ValueError(f"Góc xoay {rotation}° cần chuẩn hóa trước khi quét.")
    size = (height, width) if quarter_turns % 2 else (width, height)
    return picture, sound, size


def parse_loudness(log: str) -> dict:
    _, marker, summary = log.rpartition("Summary:")
    integrated = re.search(r"^\s*I:\s*(-?(?:\d+(?:\.\d+)?|inf))\s+LUFS", summary, re.M)
    peak = re.search(
        r"True peak:\s*Peak:\s*(-?(?:\d+(?:\.\d+)?|inf))\s+dB(?:FS|TP)",
        summary,
    )
    if not marker or integrated is None or peak is None:
        raise ValueError("Thiếu Integrated loudness hoặc True peak trong tổng kết ebur128.")
    return {
        "status": "silent" if peak[1] == "-inf" else "measured",
        "integrated_lufs": None if integrated[1] == "-inf" else float(integrated[1]),
        "true_peak_dbtp": None if peak[1] == "-inf" else float(peak[1]),
    }


def measure_loudness(video: Path, sound: dict | None) -> dict:
    if sound is None:
        return {"status": "no_audio", "integrated_lufs": None, "true_peak_dbtp": None}
    result = run_tool([
        "ffmpeg", "-hide_banner", "-nostdin", "-xerror", "-loglevel", "info", "-i", str(video),
        "-map", f"0:{sound['index']}", "-af", "ebur128=peak=true:framelog=verbose",
        "-f", "null", "-",
    ])
    return parse_loudness(result.stderr)


def edge_bar_width(profile: np.ndarray) -> int:
    """Đo dải sát mép có ít nhất 98% pixel đen và ranh giới tương phản."""
    nonblack = profile < 0.98
    if not nonblack.any():
        return 0
    width = int(nonblack.argmax())
    if not BAR_MIN_PX <= width < len(profile) / 2:
        return 0
    inner = profile[width:width + max(2, len(profile) // 100)]
    return width if inner.mean() <= 0.83 else 0


def border_widths(dark: np.ndarray) -> tuple[int, int, int, int]:
    height, width = dark.shape
    # Bỏ góc khỏi phép đo để hai loại viền có thể được nhận diện cùng lúc.
    cols = dark[:, width // 4 : width - width // 4]
    rows = dark[height // 4 : height - height // 4, :]
    vertical = np.count_nonzero(cols, axis=1) / cols.shape[1]
    horizontal = np.count_nonzero(rows, axis=0) / rows.shape[0]
    return tuple(edge_bar_width(profile) for profile in (
        vertical, vertical[::-1], horizontal, horizontal[::-1],
    ))


def blank_kind(gray: np.ndarray, dark: np.ndarray) -> str | None:
    minimum_pixels = gray.size * BLANK_FRACTION
    if cv2.countNonZero(dark) >= minimum_pixels:
        return "black"
    if cv2.countNonZero(cv2.inRange(gray, WHITE_MIN, 255)) >= minimum_pixels:
        return "white"
    return None


@dataclass
class ZoneEdges:
    box: tuple[int, int, int, int]
    densities: list[float] = field(default_factory=list)
    changes: list[float] = field(default_factory=list)
    previous: np.ndarray | None = None

    def update(self, gray: np.ndarray) -> None:
        x1, y1, x2, y2 = self.box
        edges = cv2.Canny(gray[y1:y2, x1:x2], 50, 120)
        self.densities.append(cv2.countNonZero(edges) / edges.size)
        if self.previous is not None:
            changed = cv2.bitwise_xor(edges, self.previous)
            self.changes.append(cv2.countNonZero(changed) / edges.size)
        self.previous = edges

    def report(self, times: list[float]) -> dict:
        def summarize(values: list[float], frame_offset: int) -> dict | None:
            if not values:
                return None
            index = int(np.argmax(values))
            frame = index + frame_offset
            return {
                "mean": round(float(np.mean(values)), 6),
                "max": round(values[index], 6),
                "peak_frame": frame,
                "peak_time_s": round(times[frame], 6),
            }

        return {
            "box_xyxy_exclusive": self.box,
            "edge_density": summarize(self.densities, 0),
            "edge_change_density": summarize(self.changes, 1),
        }


SHOWINFO_BASE = re.compile(rb"config in time_base:\s*(\d+/\d+)")
SHOWINFO_FRAME = re.compile(rb"\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+.*?\bs:(\d+)x(\d+)")


def frame_times(log, size: tuple[int, int]) -> list[float]:
    time_base = None
    times = []
    for line in log:
        if b"Parsed_showinfo" not in line:
            continue
        config = SHOWINFO_BASE.search(line)
        if config:
            time_base = Fraction(config[1].decode("ascii"))
        frame = SHOWINFO_FRAME.search(line)
        if frame:
            index, pts, width, height = map(int, frame.groups())
            if time_base is None or index != len(times) or (width, height) != size:
                raise ValueError("Dòng thời gian hoặc kích thước frame thay đổi khi giải mã.")
            time_s = float(pts * time_base)
            if times and time_s < times[-1]:
                raise ValueError("PTS video bị đảo thứ tự.")
            times.append(time_s)
    return times


def scan_video(video: Path, stream_index: int, size: tuple[int, int]) -> tuple:
    width, height = size
    frame_size = width * height
    zones = {name: ZoneEdges(box) for name, box in ZONES.items()} if size == VERTICAL_SIZE else {}
    blanks, lumas, borders = [], [], []
    command = [
        "ffmpeg", "-hide_banner", "-nostdin", "-xerror", "-loglevel", "info",
        "-filter_threads", "1", "-i", str(video), "-map", f"0:{stream_index}",
        "-an", "-sn", "-dn", "-vf", "format=gray,showinfo=checksum=0",
        "-fps_mode", "passthrough", "-c:v", "rawvideo", "-threads", "1",
        "-pix_fmt", "gray", "-f", "rawvideo", "pipe:1",
    ]
    with tempfile.TemporaryFile() as log:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=log) as process:
            try:
                while raw := process.stdout.read(frame_size):
                    if len(raw) != frame_size:
                        raise ValueError("FFmpeg trả về một frame thiếu dữ liệu.")
                    gray = np.frombuffer(raw, dtype=np.uint8).reshape(height, width)
                    dark = cv2.inRange(gray, 0, BLACK_MAX)
                    kind = blank_kind(gray, dark)
                    blanks.append(kind)
                    lumas.append(cv2.mean(gray)[0])
                    borders.append(border_widths(dark) if kind is None else (0, 0, 0, 0))
                    for zone in zones.values():
                        zone.update(gray)
                if process.wait():
                    log.seek(0, 2)
                    log.seek(max(0, log.tell() - 2000))
                    raise RuntimeError(f"FFmpeg không giải mã trọn video: {log.read().decode('utf-8', 'replace')}")
            finally:
                if process.poll() is None:
                    process.kill()
        log.seek(0)
        times = frame_times(log, size)
    if not times or len(times) != len(blanks):
        raise ValueError("Số frame và số mốc PTS không khớp hoặc track hình rỗng.")
    return times, blanks, lumas, borders, zones


def frame_span(start: int, stop: int, times: list[float], video_end: float) -> dict:
    end = times[stop] if stop < len(times) else video_end
    return {
        "start_frame": start,
        "end_frame": stop - 1,
        "start_time_s": round(times[start], 6),
        "end_time_s": round(end, 6),
        "duration_s": round(end - times[start], 6),
    }


def blank_events(blanks: list, lumas: list[float], times: list[float], video_end: float) -> tuple:
    ranges = []
    flashes = []
    for kind, group in groupby(enumerate(blanks), key=lambda entry: entry[1]):
        if kind is None:
            continue
        start = next(group)[0]
        stop = start + 1 + sum(1 for _ in group)
        event = {"kind": kind, **frame_span(start, stop, times, video_end)}
        ranges.append(event)

        # Một cú nháy phải ngắn và đổi độ sáng đột ngột ở các mép có frame kề.
        jumps = []
        if start > 0:
            jumps.append(abs(lumas[start] - lumas[start - 1]))
        if stop < len(blanks):
            jumps.append(abs(lumas[stop - 1] - lumas[stop]))
        if jumps and min(jumps) >= FLASH_MIN_LUMA_JUMP and event["duration_s"] <= FLASH_MAX_S:
            flashes.append(event)
    return ranges, flashes


def bar_ranges(widths: tuple, times: list[float], video_end: float) -> list[dict]:
    ranges = []
    start = 0
    for stop in range(1, len(widths) + 1):
        if stop < len(widths) and (
            (widths[start] == widths[stop] == 0)
            or (widths[stop] > 0 and widths[start] > 0
                and abs(widths[start] - widths[stop]) <= BAR_TOLERANCE_PX)
        ):
            continue
        if widths[start]:
            span = frame_span(start, stop, times, video_end)
            if stop - start >= 3 and span["duration_s"] >= BAR_MIN_S:
                ranges.append({**span, "width_px": int(round(np.median(widths[start:stop])))})
        start = stop
    return ranges


def analyze(video: Path) -> dict:
    picture, sound, (width, height) = probe(video)
    video_duration = stream_duration(video, picture)
    audio_duration = stream_duration(video, sound) if sound else None
    times, blanks, lumas, borders, zones = scan_video(video, picture["index"], (width, height))
    avg_rate = as_fraction(picture.get("avg_frame_rate"))
    fps_source = "avg_frame_rate"
    if not avg_rate or avg_rate <= 0:
        if video_duration:
            avg_rate = Fraction(len(times), 1) / Fraction(str(video_duration))
            fps_source = "decoded_frames / video_duration_s"
        else:
            avg_rate = as_fraction(picture.get("r_frame_rate"))
            fps_source = "r_frame_rate"
    fps = float(avg_rate) if avg_rate and avg_rate > 0 else None
    video_end = times[0] + video_duration if video_duration else times[-1]
    if video_end <= times[-1]:
        tail = times[-1] - times[-2] if len(times) > 1 else 0.0
        video_end = times[-1] + (tail or (1 / fps if fps else 0.0))

    blank_ranges, flashes = blank_events(blanks, lumas, times, video_end)
    bars = {
        side: bar_ranges(widths, times, video_end)
        for side, widths in zip(SIDES, zip(*borders, strict=True), strict=True)
    }
    return {
        "schema_version": 6,
        "video_path": str(video),
        "width": width,
        "height": height,
        "fps": fps,
        "fps_ratio": f"{avg_rate.numerator}/{avg_rate.denominator}" if fps else None,
        "fps_source": fps_source if fps else None,
        "decoded_frames": len(times),
        "video_duration_s": video_duration,
        "audio_duration_s": audio_duration,
        "av_delta_s": (
            round(abs(audio_duration - video_duration), 9)
            if video_duration is not None and audio_duration is not None else None
        ),
        "audio": measure_loudness(video, sound),
        "letterbox": {"present": bool(bars["top"] or bars["bottom"]), "top": bars["top"], "bottom": bars["bottom"]},
        "pillarbox": {"present": bool(bars["left"] or bars["right"]), "left": bars["left"], "right": bars["right"]},
        "blank_frame_ranges": blank_ranges,
        "boundary_flash_frames": [
            index for event in flashes for index in range(event["start_frame"], event["end_frame"] + 1)
        ],
        "boundary_flash_events": flashes,
        "safe_zone_9x16": {
            "applicable": bool(zones),
            "zones": {name: zone.report(times) for name, zone in zones.items()},
        },
    }


def write_report(output: Path, payload: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(payload)
        temporary_path.replace(output)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def self_test() -> None:
    gray = np.full((96, 120), 132, dtype=np.uint8)
    gray[:8] = gray[-6:] = 0
    gray[:, :10] = gray[:, -12:] = 0
    dark = cv2.inRange(gray, 0, BLACK_MAX)
    assert border_widths(dark) == (8, 6, 10, 12)
    assert blank_kind(gray, dark) is None
    assert border_widths(cv2.inRange(np.zeros_like(gray), 0, BLACK_MAX)) == (0, 0, 0, 0)
    assert blank_kind(np.zeros_like(gray), np.full_like(gray, 255)) == "black"
    assert blank_kind(np.full_like(gray, 255), np.zeros_like(gray)) == "white"
    assert blank_kind(np.full_like(gray, 230), np.zeros_like(gray)) is None
    times = [0.0, 0.04, 0.075, 0.10, 0.16, 0.20, 0.30, 0.40, 0.50]
    ranges, flashes = blank_events(
        [None, "black", "white", None, None, "black", "black", "black", None],
        [132, 0, 255, 132, 90, 0, 0, 0, 132], times, 0.54,
    )
    assert [event["start_frame"] for event in ranges] == [1, 2, 5]
    assert [event["start_frame"] for event in flashes] == [1, 2]
    assert not blank_events([None, "black", None], [24, 16, 24], [0, 0.04, 0.08], 0.12)[1]
    assert bar_ranges((0, 8, 9, 8, 0), [0, 0.10, 0.20, 0.30, 0.40], 0.50)[0]["width_px"] == 8
    assert not bar_ranges((8, 8, 8), [0, 0.04, 0.08], 0.12)

    canvas = np.full((1920, 1080), 120, dtype=np.uint8)
    monitors = {name: ZoneEdges(box) for name, box in ZONES.items()}
    for monitor in monitors.values():
        monitor.update(canvas)
    canvas[890:920, 890:935] = 250
    for name, monitor in monitors.items():
        monitor.update(canvas)
        result = monitor.report([0, 0.04])
        assert (result["edge_density"]["max"] > 0) == (name == "lower_right")
        assert (result["edge_change_density"]["max"] > 0) == (name == "lower_right")
    assert monitors["lower_right"].report([0, 0.04])["edge_change_density"]["peak_frame"] == 1

    log = [
        b"[Parsed_showinfo_1 @ addr] config in time_base: 1/90000, frame_rate: 30000/1001",
        b"[Parsed_showinfo_1 @ addr] n:  0 pts: -1000 pts_time:-0.0111 fmt:gray s:120x96",
        b"[Parsed_showinfo_1 @ addr] n:  1 pts:  3599 pts_time:0.0399 fmt:gray s:120x96",
    ]
    assert frame_times(log, (120, 96)) == [-1000 / 90000, 3599 / 90000]
    assert as_fraction("30000/1001") == Fraction(30000, 1001) and as_fraction("0/0") is None
    summary = "I: -99 LUFS\nSummary:\n  Integrated loudness:\n    I: -14.0 LUFS\n  True peak:\n    Peak: -1.2 dBFS\n"
    assert parse_loudness(summary) == {"status": "measured", "integrated_lufs": -14.0, "true_peak_dbtp": -1.2}
    assert parse_loudness(summary.replace("-1.2", "-inf"))["true_peak_dbtp"] is None
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--video", type=Path, help="Tệp MP4 cần kiểm duyệt.")
    source.add_argument("--self-test", action="store_true", help="Kiểm tra bằng mảng NumPy giả lập.")
    parser.add_argument("--json-out", type=Path, help="Tệp UTF-8 nhận báo cáo. Mặc định in ra stdout.")
    args = parser.parse_args()
    if args.self_test:
        if args.json_out:
            parser.error("--json-out dùng cùng --video.")
        self_test()
        return 0

    try:
        video = args.video.resolve(strict=True)
        if not video.is_file():
            raise ValueError(f"Đường dẫn video không phải tệp: {video}")
        if args.json_out and args.json_out.exists() and args.json_out.samefile(video):
            raise ValueError("--json-out trùng tệp video.")
        report = analyze(video)
        payload = json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n"
        if args.json_out:
            write_report(args.json_out, payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, RuntimeError, cv2.error) as error:
        print(f"FORENSIC_QC_ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
