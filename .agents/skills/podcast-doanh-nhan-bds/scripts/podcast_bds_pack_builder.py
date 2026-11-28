"""Đo nền âm thanh và chọn preset tiêu đề cho podcast doanh nhân, tài chính và BĐS."""

from __future__ import annotations

import argparse
from functools import partial
import json
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import wave


BGM_THRESHOLD_DBFS = -38.0
VAD_SAMPLE_RATE = 16_000
MIN_PAUSE_MS = 120
VAD_WORKER_ENV = "PODCAST_BDS_VAD_WORKER"
VAD_UNAVAILABLE = 78
TITLE_RENDERER = Path("edit/canvas-tools/podcast_bds_title.py")
MOOD_PRESETS = {
    "bds": ("magnesium_amsterdam", "gold_luxury"),
    "tai-chinh": ("barlow_artful", "cyan_ice"),
    "doanh-nhan": ("alexander_ameyallinda", "cyan_ice"),
    "triet-ly": ("braven_bengoda", "rose_satin"),
}


def studio_root() -> Path:
    for directory in Path(__file__).resolve().parents:
        if (directory / TITLE_RENDERER).is_file():
            return directory
    raise FileNotFoundError(f"Không tìm thấy {TITLE_RENDERER.as_posix()} trong Full Studio.")


def recommend_font_pair(mood: str) -> dict:
    renderer = runpy.run_path(str(studio_root() / TITLE_RENDERER))
    pair_key, theme_key = MOOD_PRESETS[mood]
    pair = renderer["PODCAST_BDS_PAIRS"][pair_key]
    theme = renderer["THEMES"][theme_key]
    colors = {
        label: "#" + bytes(theme[key][:3]).hex().upper()
        for label, key in (
            ("edge_hex", "edge_rgb"),
            ("mid_hex", "mid_rgb"),
            ("core_hex", "core_rgb"),
            ("glow_hex", "glow_rgba"),
            ("signature_glow_hex", "sub_glow_rgba"),
        )
    }
    return {"mood": mood, "pair_key": pair_key, "theme": theme_key, **pair, **colors}


def load_vad():
    from faster_whisper.vad import VadOptions, get_speech_timestamps, get_vad_model

    get_vad_model()
    return partial(
        get_speech_timestamps,
        vad_options=VadOptions(
            min_speech_duration_ms=64,
            min_silence_duration_ms=128,
            speech_pad_ms=64,
        ),
        sampling_rate=VAD_SAMPLE_RATE,
    )


def run_with_studio_vad(argv: list[str]) -> int | None:
    if os.environ.get(VAD_WORKER_ENV):
        return None

    env = {**os.environ, VAD_WORKER_ENV: "1"}
    for root in (studio_root(), Path("D:/AI/full studio")):
        python = root / "voice-studio/.venv/Scripts/python.exe"
        if not python.is_file() or python == Path(sys.executable):
            continue
        result = subprocess.run(
            [str(python), "-B", "-X", "utf8", str(Path(__file__).resolve()), *argv],
            env=env,
        )
        if result.returncode != VAD_UNAVAILABLE:
            return result.returncode
    return None


def audio_format(path: Path) -> tuple[int, int]:
    result = subprocess.check_output(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
            "stream=sample_rate,channels", "-of", "json", str(path),
        ]
    )
    streams = json.loads(result).get("streams", [])
    if not streams:
        raise ValueError("Tệp không có track âm thanh để đo.")
    sample_rate = int(streams[0]["sample_rate"])
    channels = int(streams[0]["channels"])
    if sample_rate <= 0 or channels <= 0:
        raise ValueError("Track âm thanh có sample rate hoặc số kênh không hợp lệ.")
    return sample_rate, channels


def decode_audio_command(path: Path, pcm_format: str, *options: str) -> list[str]:
    return [
        "ffmpeg", "-nostdin", "-v", "error", "-xerror", "-i", str(path),
        "-map", "0:a:0", *options, "-c:a", f"pcm_{pcm_format}",
        "-f", pcm_format, "pipe:1",
    ]


def pause_intervals(speech: list[dict], vad_frames: int, sample_rate: int) -> list[tuple[int, int]]:
    """Chuyển khoảng nghỉ sang chỉ số frame nguồn, bỏ biên chồng vào lời thoại."""
    min_frames = math.ceil(sample_rate * MIN_PAUSE_MS / 1000)
    total_frames = vad_frames * sample_rate // VAD_SAMPLE_RATE
    pauses = []
    cursor = 0
    for segment in speech:
        start = segment["start"] * sample_rate // VAD_SAMPLE_RATE
        if start - cursor >= min_frames:
            pauses.append((cursor, start))
        end = math.ceil(segment["end"] * sample_rate / VAD_SAMPLE_RATE)
        cursor = max(cursor, end)
    if total_frames - cursor >= min_frames:
        pauses.append((cursor, total_frames))
    return pauses


def measure_pause_rms(
    path: Path, sample_rate: int, channels: int, pauses: list[tuple[int, int]]
) -> float | None:
    import numpy as np

    intervals = iter(pauses)
    pause = next(intervals, None)
    frame_offset = 0
    sum_squares = 0.0
    sample_count = 0
    command = decode_audio_command(path, "f64le")
    with subprocess.Popen(command, stdout=subprocess.PIPE) as process:
        with process.stdout as audio:
            while raw := audio.read(sample_rate * channels * 8):
                frames = np.frombuffer(raw, dtype="<f8").reshape(-1, channels)
                block_end = frame_offset + len(frames)
                while pause is not None and pause[0] < block_end:
                    start, end = pause
                    samples = frames[max(start - frame_offset, 0):min(end, block_end) - frame_offset]
                    sum_squares += float(np.sum(np.square(samples), dtype=np.float64))
                    sample_count += samples.size
                    if end > block_end:
                        break
                    pause = next(intervals, None)
                frame_offset = block_end
        if process.wait() != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

    if not sample_count:
        raise ValueError("Không có đủ mẫu khoảng nghỉ để đo RMS.")
    if not math.isfinite(sum_squares):
        raise ValueError("Track âm thanh có mẫu không hữu hạn trong khoảng nghỉ.")
    if sum_squares == 0:
        return None  # JSON null biểu diễn RMS âm vô cùng của im lặng số.
    return 10 * math.log10(sum_squares / sample_count)


def probe_bgm(path: Path, detect_speech) -> dict:
    import numpy as np

    path = path.resolve(strict=True)
    if not path.is_file() or path.suffix.lower() not in {".wav", ".mp4"}:
        raise ValueError("--probe-bgm cần một tệp WAV hoặc MP4.")

    sample_rate, channels = audio_format(path)
    vad_command = decode_audio_command(path, "f32le", "-ar", str(VAD_SAMPLE_RATE))
    audio = np.frombuffer(subprocess.check_output(vad_command), dtype="<f4").reshape(-1, channels)
    if len(audio) < VAD_SAMPLE_RATE * MIN_PAUSE_MS // 1000:
        raise ValueError(f"Track âm thanh ngắn hơn {MIN_PAUSE_MS} ms.")
    if not np.isfinite(audio).all():
        raise ValueError("Track âm thanh có mẫu không hữu hạn.")

    speech = []
    for channel in audio.T:
        speech.extend(detect_speech(np.ascontiguousarray(channel)))
    speech.sort(key=lambda segment: segment["start"])
    pauses = pause_intervals(speech, len(audio), sample_rate)
    if not pauses:
        raise ValueError(f"Không tìm được khoảng nghỉ thoại dài ít nhất {MIN_PAUSE_MS} ms.")

    rms_dbfs = measure_pause_rms(path, sample_rate, channels, pauses)
    has_existing_bgm = rms_dbfs is not None and rms_dbfs > BGM_THRESHOLD_DBFS
    return {
        "non_speech_rms_dbfs": rms_dbfs,
        "has_existing_bgm": has_existing_bgm,
        "allow_new_bgm": not has_existing_bgm,
    }


def self_test(detect_speech) -> None:
    import numpy as np

    sample_rate = 48_000
    t = np.arange(sample_rate * 2) / sample_rate
    room_tone = np.random.default_rng(42).standard_normal(t.size)
    music_bed = np.sin(2 * np.pi * 130 * t) + 0.5 * np.sin(2 * np.pi * 195 * t)
    with tempfile.TemporaryDirectory(prefix="podcast-bds-test-", dir=Path.cwd()) as tmp:
        for expected_rms, bed, has_bgm in ((-55.0, room_tone, False), (-31.0, music_bed, True)):
            path = Path(tmp) / f"background_{expected_rms:g}.wav"
            normalized = bed * (10 ** (expected_rms / 20) / np.sqrt(np.mean(np.square(bed))))
            # Nửa sau đảo pha để kiểm tra RMS kênh độc lập.
            right = normalized.copy()
            right[len(right) // 2:] *= -1
            stereo = np.column_stack((normalized, right))
            pcm = np.rint(stereo * 32768).astype("<i2")
            with wave.open(str(path), "wb") as wav:
                wav.setparams((2, 2, sample_rate, 0, "NONE", "not compressed"))
                wav.writeframes(pcm.tobytes())

            result = probe_bgm(path, detect_speech)
            measured = result["non_speech_rms_dbfs"]
            if measured is None or not math.isclose(measured, expected_rms, abs_tol=0.01):
                raise RuntimeError(f"Self-test RMS {expected_rms:g} dBFS nhận {measured!r}.")
            if result["has_existing_bgm"] != has_bgm or result["allow_new_bgm"] == has_bgm:
                raise RuntimeError(f"Self-test quy tắc BGM {expected_rms:g} dBFS nhận {result!r}.")
    print("SELF_TEST_OK")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--probe-bgm", metavar="WAV_OR_MP4", type=Path,
        help="Đo RMS khoảng nghỉ thoại và kiểm tra BGM.",
    )
    action.add_argument(
        "--recommend-font-pair", metavar="MOOD", choices=MOOD_PRESETS,
        help="Chọn cặp font và màu theo mood (bds, tai-chinh, doanh-nhan, triet-ly).",
    )
    action.add_argument("--self-test", action="store_true", help="Kiểm tra WAV giả lập ở -55 và -31 dBFS.")
    args = parser.parse_args(argv)

    try:
        if args.recommend_font_pair:
            print(json.dumps(recommend_font_pair(args.recommend_font_pair), ensure_ascii=False))
            return 0

        try:
            detect_speech = load_vad()
        except (ImportError, OSError, RuntimeError) as error:
            status = run_with_studio_vad(argv)
            if status is not None:
                return status
            if not os.environ.get(VAD_WORKER_ENV):
                print(f"Cần faster-whisper 1.2.1 và onnxruntime để chạy Silero VAD: {error}", file=sys.stderr)
            return VAD_UNAVAILABLE

        if args.self_test:
            self_test(detect_speech)
        else:
            print(json.dumps(probe_bgm(args.probe_bgm, detect_speech), allow_nan=False))
        return 0
    except (ImportError, OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Lỗi: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
