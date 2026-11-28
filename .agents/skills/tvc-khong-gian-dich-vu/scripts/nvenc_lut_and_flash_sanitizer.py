#!/usr/bin/env python3
"""Grade one SDR source clip with a .cube LUT and remove isolated edge flashes."""

from __future__ import annotations

import argparse
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
from statistics import median
import subprocess
from tempfile import TemporaryDirectory


BASELINE_FRAMES = 3
MAX_FLASH_FRAMES = 2
LUMA_JUMP = 28
BASELINE_SPREAD = 10
EDGE_WINDOW = BASELINE_FRAMES + MAX_FLASH_FRAMES
SHOWINFO_FRAME = re.compile(
    r"\bn:\s*(\d+)\s+pts:\s*(-?\d+)\b.*?\bmean:\s*\[\s*(\d+)"
)


@dataclass(frozen=True)
class Frame:
    pts_us: int
    luma: int


@dataclass(frozen=True)
class Edges:
    first: tuple[Frame, ...]
    last: tuple[Frame, ...]
    count: int


@dataclass(frozen=True)
class Trim:
    start_frame: int = 0
    end_frame: int | None = None  # exclusive
    start_us: int | None = None
    end_us: int | None = None


def collect_edges(lines: Iterable[str]) -> Edges:
    first: list[Frame] = []
    last: deque[Frame] = deque(maxlen=EDGE_WINDOW)
    count = 0
    invalid = False
    for line in lines:
        if "Parsed_showinfo_" not in line:
            continue
        match = SHOWINFO_FRAME.search(line)
        if match is None:
            continue

        index, pts_us, luma = map(int, match.groups())
        if index != count or (last and pts_us <= last[-1].pts_us):
            invalid = True
        frame = Frame(pts_us, luma)
        if count < EDGE_WINDOW:
            first.append(frame)
        last.append(frame)
        count += 1

    if invalid:
        raise ValueError("Non-monotonic frame timestamps or a video format change during analysis.")
    if not count:
        raise ValueError("No decoded video frames with valid luma and timestamps were found.")
    return Edges(tuple(first), tuple(last), count)


def scan_edges(ffmpeg: str, source: Path) -> Edges:
    command = [
        ffmpeg, "-hide_banner", "-nostdin", "-nostats", "-loglevel", "info",
        "-xerror", "-i", str(source), "-map", "0:V:0", "-an", "-sn", "-dn",
        "-vf", "settb=AVTB,scale=64:36:flags=area,format=yuv444p,showinfo",
        "-fps_mode", "passthrough", "-enc_time_base:v", "filter", "-f", "null", "-",
    ]
    diagnostics: deque[str] = deque(maxlen=12)
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        encoding="utf-8", errors="replace",
    ) as process:
        assert process.stdout is not None

        def log_lines() -> Iterable[str]:
            for line in process.stdout:
                diagnostics.append(line.rstrip())
                yield line

        try:
            edges = collect_edges(log_lines())
        except ValueError as error:
            if process.wait() != 0:
                raise ValueError("FFmpeg analysis failed.\n" + "\n".join(diagnostics)) from error
            raise
        if process.wait():
            raise ValueError("FFmpeg analysis failed.\n" + "\n".join(diagnostics))
        return edges


def flash_count(edge: Sequence[Frame], maximum: int) -> int:
    """Read from the boundary inwards, looking for a brief bright or dark step."""
    for count in range(1, maximum + 1):
        baseline = [frame.luma for frame in edge[count:count + BASELINE_FRAMES]]
        if len(baseline) < BASELINE_FRAMES or max(baseline) - min(baseline) > BASELINE_SPREAD:
            continue

        reference = median(baseline)
        deviations = [frame.luma - reference for frame in edge[:count]]
        join_jump = edge[count - 1].luma - edge[count].luma
        if min(deviations) >= LUMA_JUMP and join_jump >= LUMA_JUMP:
            return count
        if max(deviations) <= -LUMA_JUMP and join_jump <= -LUMA_JUMP:
            return count
    return 0


def plan_trim(edges: Edges, maximum: int) -> Trim:
    head = flash_count(edges.first, maximum)
    tail = flash_count(edges.last[::-1], maximum)
    if edges.count - head - tail < BASELINE_FRAMES:
        return Trim()
    return Trim(
        start_frame=head,
        end_frame=edges.count - tail if tail else None,
        start_us=edges.first[head].pts_us if head else None,
        end_us=edges.last[-tail].pts_us if tail else None,
    )


def build_encode_command(ffmpeg: str, source: Path, output: Path, trim: Trim) -> list[str]:
    # The caller runs this in a temporary directory containing grade.cube.
    # Its fixed basename avoids FFmpeg's two filtergraph escaping levels on Windows.
    video_filters = []
    audio_options = []
    if trim.start_frame or trim.end_frame is not None:
        frame_bounds = [f"start_frame={trim.start_frame}"]
        audio_bounds = []
        if trim.start_us is not None:
            audio_bounds.append(f"start={trim.start_us}us")
        if trim.end_frame is not None:
            frame_bounds.append(f"end_frame={trim.end_frame}")
            audio_bounds.append(f"end={trim.end_us}us")
        video_filters.append("trim=" + ":".join(frame_bounds))
        audio_filter = "atrim=" + ":".join(audio_bounds)
        if trim.start_us is not None:
            video_filters.append("setpts=PTS-STARTPTS")
            # Use the same origin for both streams, including delayed audio tracks.
            audio_filter += f",asetpts=PTS-round({trim.start_us}/(1000000*TB))"
        audio_options = ["-af", audio_filter]

    video_filters.extend([
        "format=gbrp16le", "lut3d=file=grade.cube:interp=tetrahedral",
        "pad=ceil(iw/2)*2:ceil(ih/2)*2",
    ])
    command = [
        ffmpeg, "-hide_banner", "-nostdin", "-n", "-loglevel", "warning", "-xerror",
        "-i", str(source), "-map", "0:V:0", "-map", "0:a?", "-map_chapters", "-1",
        "-vf", ",".join(video_filters), *audio_options,
        "-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "18", "-b:v", "0",
        "-pix_fmt", "yuv420p", "-fps_mode", "passthrough", "-enc_time_base:v", "filter",
        "-c:a", "aac", "-b:a", "192k",
    ]
    if output.suffix.lower() in {".mp4", ".mov", ".m4v"}:
        command += ["-movflags", "+faststart"]
    return [*command, str(output)]


def sanitize(source: Path, lut: Path, output: Path, maximum: int) -> None:
    source, lut, output = (path.resolve() for path in (source, lut, output))
    if not source.is_file():
        raise ValueError(f"Input clip does not exist: {source}")
    if not lut.is_file() or lut.suffix.lower() != ".cube":
        raise ValueError(f"Expected an existing .cube LUT: {lut}")
    if not output.suffix:
        raise ValueError("Output needs a video container extension, for example .mp4.")
    if output.exists():
        raise ValueError(f"Output already exists: {output}")
    ffmpeg_found = shutil.which("ffmpeg")
    if ffmpeg_found is None:
        raise ValueError("FFmpeg was not found on PATH. Use an FFmpeg 6.1+ build with h264_nvenc.")
    ffmpeg = str(Path(ffmpeg_found).resolve())

    trim = Trim()
    if maximum:
        edges = scan_edges(ffmpeg, source)
        trim = plan_trim(edges, maximum)
        tail = edges.count - trim.end_frame if trim.end_frame is not None else 0
        print(f"FLASH_TRIM head={trim.start_frame} tail={tail} analyzed={edges.count}", flush=True)

    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".nvenc-lut-", dir=output.parent) as temporary:
        work = Path(temporary)
        shutil.copyfile(lut, work / "grade.cube")
        encoded = work / ("encoded" + output.suffix)
        subprocess.run(build_encode_command(ffmpeg, source, encoded, trim), cwd=work, check=True)
        if os.name == "nt":
            encoded.rename(output)  # Atomic move on Windows, failing if the destination exists.
        else:
            os.link(encoded, output)  # Atomic publication without overwriting on POSIX.
    print(f"OUTPUT {output}")


def self_test() -> None:
    def synthetic_edges(lumas: Sequence[int]) -> Edges:
        # Uneven times simulate a VFR source without starting FFmpeg.
        return collect_edges(
            f"[Parsed_showinfo_3 @ 0001] n:{index:4} pts:{index * 33667 + index % 2:7} "
            f"pts_time:0 mean:[{luma} 128 128]"
            for index, luma in enumerate(lumas)
        )

    cases = [
        ([231, 214, 82, 81, 84, 80, 83, 15], 2, 2, 7),
        ([17, 83, 82, 84, 82, 80, 216, 229], 2, 1, 6),
        ([87, 83, 84, 84, 229, 81, 84, 86, 85, 85, 87], 2, 0, None),
        ([40, 54, 69, 82, 84, 82, 82], 2, 0, None),
        ([231, 214, 82, 81, 84], 1, 0, None),
        ([231, 82, 80], 2, 0, None),
        ([82, 82, 83, 225], 2, 0, 3),
        ([231, 82, 81, 83], 0, 0, None),
    ]
    for lumas, maximum, head, end in cases:
        trim = plan_trim(synthetic_edges(lumas), maximum)
        expected = Trim(
            head, end, head * 33667 + head % 2 if head else None,
            end * 33667 + end % 2 if end is not None else None,
        )
        if trim != expected:
            raise AssertionError(f"Luma {lumas} yielded {trim}, expected {expected}.")

    source = Path("C:/TVC Việt/clip nguồn.mp4")
    output = Path("C:/TVC Việt/bản màu.mp4")
    trim = plan_trim(synthetic_edges(cases[0][0]), 2)
    command = build_encode_command("ffmpeg", source, output, trim)
    expected_options = {
        "-i": str(source), "-c:v": "h264_nvenc", "-preset": "p5", "-rc": "vbr",
        "-cq": "18", "-movflags": "+faststart", "-fps_mode": "passthrough",
        "-vf": "trim=start_frame=2:end_frame=7,setpts=PTS-STARTPTS,format=gbrp16le,"
               "lut3d=file=grade.cube:interp=tetrahedral,pad=ceil(iw/2)*2:ceil(ih/2)*2",
        "-af": "atrim=start=67334us:end=235670us,asetpts=PTS-round(67334/(1000000*TB))",
    }
    for option, value in expected_options.items():
        if command[command.index(option) + 1] != value:
            raise AssertionError(f"Unexpected value for {option} in {command!r}.")
    tail_only = build_encode_command("ffmpeg", source, output, Trim(end_frame=3, end_us=101002))
    untrimmed = build_encode_command("ffmpeg", source, output, Trim())
    if (command[-1] != str(output) or "-af" in untrimmed
            or "trim=" in untrimmed[untrimmed.index("-vf") + 1]
            or tail_only[tail_only.index("-af") + 1] != "atrim=end=101002us"
            or "setpts=" in tail_only[tail_only.index("-vf") + 1]):
        raise AssertionError("Invalid output path or trimming on an unchanged boundary.")
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Source video clip (SDR, with optional audio).")
    parser.add_argument("--lut", type=Path, help="Input .cube 3D LUT matched to the source color space.")
    parser.add_argument("--output", type=Path, help="New output video path, typically .mp4.")
    parser.add_argument(
        "--trim-flash-frames", type=int, nargs="?", const=2, default=2, choices=(0, 1, 2),
        help="Maximum frames removed per edge when a flash is detected (default 2, 0 skips detection).",
    )
    parser.add_argument("--self-test", action="store_true", help="Test detection and command generation offline.")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.input is None or args.lut is None or args.output is None:
        parser.error("--input, --lut and --output are required unless --self-test is used.")
    try:
        sanitize(args.input, args.lut, args.output, args.trim_flash_frames)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
