#!/usr/bin/env python3
"""Master và kiểm tra âm lượng quảng cáo với Python 3.11 và FFmpeg."""

import argparse
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile


TARGET_I = -11.0
TARGET_TP = -1.0
TARGET_LRA = 7
MIN_I = -11.4
MAX_I = -10.5
OUTPUT_FORMATS = {".mp4", ".mov", ".wav"}
MAX_ENCODES = 3


@dataclass(frozen=True)
class Loudness:
    integrated: float
    true_peak: float
    range: float
    threshold: float
    offset: float

    def summary(self) -> str:
        return (
            f"I={self.integrated:.2f} LUFS, TP={self.true_peak:.2f} dBTP, "
            f"LRA={self.range:.2f} LU"
        )

    def failures(self) -> list[str]:
        issues = []
        if not MIN_I <= self.integrated <= MAX_I:
            issues.append(f"I ngoài [{MIN_I}, {MAX_I}] LUFS")
        if self.true_peak > TARGET_TP:
            issues.append(f"TP vượt {TARGET_TP:.1f} dBTP")
        if self.range > TARGET_LRA:
            issues.append(f"LRA vượt {TARGET_LRA} LU")
        return issues


def loudnorm(target_tp: float = TARGET_TP) -> str:
    return f"loudnorm=I={TARGET_I:.1f}:TP={target_tp}:LRA={TARGET_LRA}"


def run_ffmpeg(executable: str, source: Path, arguments: list[str]) -> str:
    command = [
        executable, "-hide_banner", "-nostats", "-nostdin", "-loglevel", "info",
        "-i", str(source), *arguments,
    ]
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode:
        tail = "\n".join(result.stderr.strip().splitlines()[-10:])
        raise ValueError(f"FFmpeg thoát mã {result.returncode} khi đọc {source.name}.\n{tail}")
    return result.stderr


def read_stats(log: str) -> dict[str, str]:
    blocks = re.findall(r'\{[^{}]*"input_i"\s*:[^{}]*\}', log)
    if not blocks:
        raise ValueError("FFmpeg không trả về JSON loudnorm.")
    return json.loads(blocks[-1])


def measure(ffmpeg: str, source: Path) -> Loudness:
    log = run_ffmpeg(ffmpeg, source, [
        "-map", "0:a:0", "-af", f"{loudnorm()}:print_format=json", "-f", "null", "-",
    ])
    stats = read_stats(log)
    measured = Loudness(*(float(stats[key]) for key in (
        "input_i", "input_tp", "input_lra", "input_thresh", "target_offset",
    )))
    if not all(math.isfinite(value) for value in (
        measured.integrated, measured.true_peak, measured.range,
        measured.threshold, measured.offset,
    )):
        raise ValueError("Không đo được loudness hữu hạn. Hãy kiểm tra track âm thanh và đoạn im lặng.")
    return measured


def encode(ffmpeg: str, source: Path, temporary: Path, measured: Loudness, target_tp: float) -> str:
    audio_filter = (
        f"{loudnorm(target_tp)}:measured_I={measured.integrated}"
        f":measured_TP={measured.true_peak}:measured_LRA={measured.range}"
        f":measured_thresh={measured.threshold}:offset={measured.offset}"
        ":linear=true:print_format=json"
    )
    if temporary.suffix.lower() == ".wav":
        video = []
        audio = ["-c:a", "pcm_s24le"]
    else:
        video = ["-map", "0:V:0", "-c:v", "copy", "-movflags", "+faststart"]
        audio = ["-c:a", "aac", "-b:a", "320k"]
    log = run_ffmpeg(ffmpeg, source, [
        *video, "-map", "0:a:0", "-af", audio_filter, "-ar", "48000", *audio,
        "-y", str(temporary),
    ])
    return read_stats(log)["normalization_type"]


def publish(temporary: Path, output: Path, overwrite: bool) -> None:
    if overwrite:
        temporary.replace(output)
    elif os.name == "nt":
        temporary.rename(output)
    else:
        # A concurrent job may have created the destination after validation.
        os.link(temporary, output)


def master(ffmpeg: str, source: Path, output: Path, overwrite: bool) -> None:
    if output.suffix.lower() not in OUTPUT_FORMATS:
        raise ValueError("Đuôi đầu ra phải là .mp4, .mov hoặc .wav.")
    if source == output or (output.exists() and source.samefile(output)):
        raise ValueError("Đầu ra phải khác tệp đầu vào.")
    if output.exists() and not overwrite:
        raise FileExistsError(f"Đầu ra đã tồn tại. Dùng --overwrite nếu muốn thay thế. {output}")
    if not output.parent.is_dir():
        raise ValueError(f"Thư mục đầu ra chưa tồn tại. {output.parent}")

    measured = measure(ffmpeg, source)
    print(f"Lượt 1 · nguồn · {measured.summary()}", flush=True)
    target_tp = TARGET_TP
    with tempfile.NamedTemporaryFile(
        dir=output.parent, prefix=".loudnorm-", suffix=output.suffix, delete=False,
    ) as handle:
        temporary = Path(handle.name)

    try:
        for attempt in range(1, MAX_ENCODES + 1):
            mode = encode(ffmpeg, source, temporary, measured, target_tp)
            final = measure(ffmpeg, temporary)
            print(
                f"Lượt 2 · lần {attempt} · {mode} · TP đích {target_tp:.2f} dBTP",
                flush=True,
            )
            print(f"QC tệp đã mã hóa · {final.summary()}", flush=True)
            issues = final.failures()
            if not issues:
                publish(temporary, output, overwrite)
                print(f"ĐẠT · {output}")
                return
            if final.true_peak <= TARGET_TP or attempt == MAX_ENCODES:
                break
            # AAC và resampling có thể thay đổi true peak sau loudnorm.
            target_tp = round(target_tp - (final.true_peak - TARGET_TP) - 0.10, 2)
            if target_tp < -9.0:
                break
        raise ValueError("QC không đạt · " + ", ".join(issues))
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Video hoặc bản mix stereo/mono đầu vào.")
    parser.add_argument("output", type=Path, nargs="?", help="Tệp .mp4, .mov hoặc .wav cần xuất.")
    parser.add_argument("--verify-only", action="store_true", help="Đo QC tệp đầu vào đã mã hóa.")
    parser.add_argument("--overwrite", action="store_true", help="Chỉ thay đầu ra cũ sau khi QC đạt.")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="Tên lệnh hoặc đường dẫn FFmpeg.")
    args = parser.parse_args()
    if args.verify_only and (args.output is not None or args.overwrite):
        parser.error("--verify-only chỉ nhận tệp đầu vào và tùy chọn --ffmpeg.")
    if not args.verify_only and args.output is None:
        parser.error("Cần tên tệp đầu ra hoặc --verify-only.")

    try:
        source = args.input.resolve(strict=True)
        if not source.is_file():
            raise ValueError(f"Đầu vào phải là một tệp. {source}")
        if args.verify_only:
            final = measure(args.ffmpeg, source)
            print(f"QC · {final.summary()}", flush=True)
            if issues := final.failures():
                raise ValueError("QC không đạt · " + ", ".join(issues))
            print(f"ĐẠT · {source}")
        else:
            master(args.ffmpeg, source, args.output.resolve(), args.overwrite)
    except (OSError, ValueError, KeyError) as exc:
        print(f"LỖI · {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
