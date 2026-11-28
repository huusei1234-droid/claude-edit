"""Analyze a reference video's cuts, camera motion, and colors for HyperFrames."""

import argparse
from collections import Counter
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

import cv2
import numpy as np


ANALYSIS_EDGE = 320
COLOR_BINS = 16**3


def probe_video(path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "V:0",
                "-show_entries", "stream=avg_frame_rate,r_frame_rate,duration",
                "-of", "json", str(path),
            ],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError as error:
        raise ValueError("ffprobe is required on PATH") from error
    if result.returncode:
        raise ValueError(result.stderr.strip() or f"ffprobe exited with {result.returncode}")
    streams = json.loads(result.stdout).get("streams", [])
    if not streams:
        raise ValueError(f"No video stream found in {path}")
    return streams[0]


def read_frame_rate(*values):
    for value in values:
        try:
            rate = Fraction(str(value))
        except (ValueError, ZeroDivisionError):
            continue
        if isinstance(value, float):
            rate = rate.limit_denominator(100_000)
        if rate > 0:
            return rate
    raise ValueError("Could not determine a positive video frame rate")


def iter_video_frames(capture):
    while True:
        ok, frame = capture.read()
        if not ok:
            return
        yield frame, capture.get(cv2.CAP_PROP_POS_MSEC) / 1_000


def resize_for_analysis(frame):
    height, width = frame.shape[:2]
    scale = ANALYSIS_EDGE / max(height, width)
    if scale >= 1:
        return frame
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return cv2.resize(frame, size, interpolation=cv2.INTER_AREA)


def cut_histogram(frame):
    hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)
    return hist / (frame.shape[0] * frame.shape[1])


def is_hard_cut(previous, current, previous_gray, gray, hist_delta):
    luma_delta = np.mean(cv2.absdiff(previous_gray, gray)) / 255
    if hist_delta >= 0.38 and luma_delta >= 0.13:
        return True
    # Adjacent shots can have very different colors at the same luminance.
    return hist_delta >= 0.68 and np.mean(cv2.absdiff(previous, current)) / 255 >= 0.17


def camera_motion(previous_gray, gray, grid):
    if len(grid) < 12 or np.array_equal(previous_gray, gray):
        return "STATIC"

    height, width = gray.shape
    flow = cv2.calcOpticalFlowFarneback(previous_gray, gray, None, 0.5, 3, 21, 3, 5, 1.2, 0)
    x, y = grid.T
    texture = cv2.cornerMinEigenVal(previous_gray, blockSize=7)[y, x]
    textured = texture >= max(1e-5, float(np.percentile(texture, 75)) * 0.15)
    points = grid[textured].astype(np.float32)
    if len(points) < 12:
        return "STATIC"

    target = points + flow[y[textured], x[textured]]
    transform, inliers = cv2.estimateAffinePartial2D(
        points, target, method=cv2.RANSAC, ransacReprojThreshold=0.75,
    )
    if transform is None or np.mean(inliers) < 0.55:
        return "STATIC"
    support = points[inliers.ravel().astype(bool)]
    if len(support) < 12 or np.any(np.ptp(support, axis=0) < np.array([width, height]) * 0.45):
        return "STATIC"

    center = np.array([(width - 1) / 2, (height - 1) / 2])
    shift_x, shift_y = transform[:, :2] @ center + transform[:, 2] - center
    translation = math.hypot(shift_x, shift_y)
    scale = math.hypot(transform[0, 0], transform[1, 0])
    radius = math.hypot(*center)
    zoom_at_edge = abs(scale - 1) * radius
    motion_floor = max(0.18, radius * 0.0015)

    if zoom_at_edge > max(motion_floor, translation):
        return "PUSH_IN" if scale > 1 else "PULL_OUT"
    if translation <= motion_floor:
        return "STATIC"
    # A camera turn shifts image features in the opposite direction.
    if abs(shift_x) >= abs(shift_y):
        return "PAN_LEFT" if shift_x > 0 else "PAN_RIGHT"
    return "TILT_UP" if shift_y > 0 else "TILT_DOWN"


class Shot:
    def __init__(self, start_frame):
        self.start_frame = start_frame
        self.motion_votes = Counter()
        self.color_counts = np.zeros(COLOR_BINS, dtype=np.int64)
        self.color_sums = np.zeros((COLOR_BINS, 3))

    def sample_color(self, frame):
        small = resize_palette_sample(frame)
        rgb = small[:, :, ::-1].reshape(-1, 3)
        bins = rgb.astype(np.int32) >> 4
        indices = bins[:, 0] * 256 + bins[:, 1] * 16 + bins[:, 2]
        self.color_counts += np.bincount(indices, minlength=COLOR_BINS)
        for channel in range(3):
            self.color_sums[:, channel] += np.bincount(
                indices, weights=rgb[:, channel], minlength=COLOR_BINS,
            )

    def palette(self):
        occupied = self.color_counts > 0
        counts = self.color_counts[occupied]
        sums = self.color_sums[occupied]
        centers = sums / counts[:, None]
        palette = []
        while len(counts) and len(palette) < 5:
            peak = centers[np.argmax(counts)]
            nearby = np.linalg.norm(centers - peak, axis=1) <= 28
            rgb = np.rint(sums[nearby].sum(axis=0) / counts[nearby].sum()).astype(int)
            palette.append(f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}")
            counts, sums, centers = counts[~nearby], sums[~nearby], centers[~nearby]
        return palette + [palette[-1]] * (5 - len(palette))

    def finish(self, end_frame):
        return {
            "start_frame": self.start_frame,
            "end_frame": end_frame,
            "camera_motion": self.motion_votes.most_common(1)[0][0] if self.motion_votes else "STATIC",
            "dominant_hex_palette": self.palette(),
        }


def resize_palette_sample(frame):
    height, width = frame.shape[:2]
    scale = min(1, 64 / max(height, width))
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    # Sample original colors instead of averaging distinct colors into a new one.
    return cv2.resize(frame, size, interpolation=cv2.INTER_NEAREST)


def resolve_timeline(positions, fps, stream_duration):
    nominal = np.arange(len(positions), dtype=np.float64) / float(fps)
    frame_step = 1 / float(fps)
    timestamps = np.asarray(positions, dtype=np.float64)
    timestamps -= timestamps[0]
    gaps = np.diff(timestamps)
    if (
        len(gaps)
        and np.all(np.isfinite(timestamps))
        and np.all(gaps > 0)
        and np.max(np.abs(timestamps - nominal)) > max(0.002, frame_step * 0.1)
    ):
        end = timestamps[-1] + gaps[-1]
        if stream_duration is not None and timestamps[-1] < stream_duration:
            end = stream_duration
        return np.append(timestamps, end), "source_timestamps"
    return np.append(nominal, len(positions) / float(fps)), "frame_index_over_fps"


def analyze_frames(frames, fps, stream_duration=None):
    positions = []
    shots = []
    shot = Shot(0)
    color_stride = max(1, round(float(fps) / 4))
    previous = None

    for index, (frame, timestamp) in enumerate(frames):
        positions.append(timestamp)
        current = resize_for_analysis(frame)
        gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)
        histogram = cut_histogram(current)
        if previous is None:
            height, width = frame.shape[:2]
            y, x = np.mgrid[4:gray.shape[0] - 4:6, 4:gray.shape[1] - 4:6]
            grid = np.column_stack((x.ravel(), y.ravel()))
        else:
            previous_frame, previous_gray, previous_histogram = previous
            hist_delta = np.abs(histogram - previous_histogram).sum() / 2
            if is_hard_cut(previous_frame, current, previous_gray, gray, hist_delta):
                shots.append(shot.finish(index))
                shot = Shot(index)
            else:
                shot.motion_votes[camera_motion(previous_gray, gray, grid)] += 1

        if (index - shot.start_frame) % color_stride == 0:
            shot.sample_color(frame)
        previous = current, gray, histogram

    frame_count = len(positions)
    if not frame_count:
        raise ValueError("OpenCV could not decode any video frames")
    shots.append(shot.finish(frame_count))
    times, timing_source = resolve_timeline(positions, fps, stream_duration)
    duration = float(times[-1])
    for scene in shots:
        start = float(times[scene["start_frame"]])
        end = float(times[scene["end_frame"]])
        scene["start_seconds"] = round(start, 9)
        scene["end_seconds"] = round(end, 9)
        scene["duration_seconds"] = round(end - start, 9)

    cuts = [{"frame": scene["start_frame"], "time_s": scene["start_seconds"]} for scene in shots[1:]]
    return {
        "schema_version": 6,
        "video": {
            "width": width,
            "height": height,
            "fps": float(fps),
            "fps_fraction": str(fps),
            "frame_count": frame_count,
            "duration_seconds": round(duration, 9),
            "timing_source": timing_source,
        },
        "shot_boundaries": cuts,
        "avg_asl_seconds": round(duration / len(shots), 9),
        "cuts_per_minute": round(len(cuts) * 60 / duration, 6),
        "beat_grid_s": [scene["start_seconds"] for scene in shots],
        "shots": shots,
    }


def analyze_video(path):
    stream = probe_video(path)
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError(f"OpenCV could not open {path}")
        fps = read_frame_rate(stream.get("avg_frame_rate"), stream.get("r_frame_rate"), capture.get(cv2.CAP_PROP_FPS))
        try:
            stream_duration = float(stream.get("duration", "nan"))
        except ValueError:
            stream_duration = math.nan
        blueprint = analyze_frames(
            iter_video_frames(capture), fps, stream_duration if math.isfinite(stream_duration) else None,
        )
    finally:
        capture.release()
    blueprint["video"]["source"] = str(path)
    return blueprint


def write_blueprint(path, blueprint):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent, suffix=".tmp", delete=False,
        ) as file:
            temporary = Path(file.name)
            json.dump(blueprint, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def self_test():
    fps = Fraction(12)
    rng = np.random.default_rng(6)
    still = rng.integers(10, 80, (96, 160, 3), dtype=np.uint8)
    panorama = rng.integers(125, 255, (96, 198, 3), dtype=np.uint8)
    panorama = cv2.GaussianBlur(panorama, (3, 3), 0)
    frames = [still] * 8 + [panorama[:, offset:offset + 160] for offset in range(0, 36, 3)]
    blueprint = analyze_frames(((frame, index / float(fps)) for index, frame in enumerate(frames)), fps)
    assert blueprint["shot_boundaries"] == [{"frame": 8, "time_s": round(8 / float(fps), 9)}], blueprint
    assert [scene["camera_motion"] for scene in blueprint["shots"]] == ["STATIC", "PAN_RIGHT"], blueprint
    assert blueprint["beat_grid_s"] == [0, round(8 / float(fps), 9)], blueprint
    assert blueprint["shots"][-1]["end_frame"] == len(frames), blueprint
    for scene in blueprint["shots"]:
        palette = scene["dominant_hex_palette"]
        assert len(palette) == 5 and all(len(color) == 7 and color.startswith("#") for color in palette), palette
    print("SELF_TEST_OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--video", type=Path, help="Local reference video")
    mode.add_argument("--self-test", action="store_true", help="Check synthetic cuts and motion in memory")
    parser.add_argument("--out", type=Path, default=Path("reverse_blueprint.json"), help="Output JSON path")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return

    video = args.video.resolve()
    output = args.out.resolve()
    if not video.is_file():
        parser.error(f"Video does not exist or is not a file: {video}")
    if video == output:
        parser.error("--out must be a different file from --video")
    try:
        write_blueprint(output, analyze_video(video))
    except (OSError, ValueError, cv2.error) as error:
        parser.exit(1, f"error: {error}\n")
    print(output)


if __name__ == "__main__":
    main()
