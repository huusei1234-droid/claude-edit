"""Normalize product cutouts and verify retouching on aligned, 8-bit PNGs."""

import argparse
import json
import os
import re
import tempfile
from contextlib import redirect_stdout
from io import BytesIO, StringIO
from itertools import product
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms, ImageFilter, ImageOps


Box = tuple[int, int, int, int]  # Left, top, right, bottom; right and bottom excluded.
DETAIL_RADIUS = 2
MIN_PORE_RETENTION = 92.0
SRGB = ImageCms.createProfile("sRGB")


def parse_canvas(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([1-9][0-9]*)[xX]([1-9][0-9]*)", value)
    if not match:
        raise argparse.ArgumentTypeError("expected positive WIDTHxHEIGHT, e.g. 1200x1200")
    return int(match[1]), int(match[2])


def parse_box(value: str) -> Box:
    match = re.fullmatch(r"([0-9]+),([0-9]+),([1-9][0-9]*),([1-9][0-9]*)", value)
    if not match:
        raise argparse.ArgumentTypeError("expected x,y,w,h with nonnegative x,y and positive w,h")
    x, y, width, height = map(int, match.groups())
    return x, y, x + width, y + height


def parse_fill_ratio(value: str) -> float:
    ratio = float(value)
    if not 0 < ratio <= 1:
        raise argparse.ArgumentTypeError("expected a fill ratio in (0, 1]")
    return ratio


def read_cutout(path: Path) -> tuple[Image.Image, bytes | None]:
    with Image.open(path) as image:
        if image.format != "PNG" or ("A" not in image.getbands() and "transparency" not in image.info):
            raise ValueError(f"{path.name}: expected a PNG with an alpha channel or transparency")
        icc = image.info.get("icc_profile")
        image = ImageOps.exif_transpose(image).convert("RGBA")
        bounds = image.getchannel("A").getbbox()
        if bounds is None:
            raise ValueError(f"{path.name}: alpha is completely transparent")
        return image.crop(bounds), icc


def optical_offset(alpha: Image.Image, canvas: tuple[int, int]) -> tuple[int, int]:
    coverage = np.asarray(alpha)
    offset = []
    for weights, canvas_size in zip((coverage.sum(axis=0), coverage.sum(axis=1)), canvas):
        subject_size = len(weights)
        centroid = np.average(np.arange(subject_size) + 0.5, weights=weights)
        offset.append(max(0, min(round(canvas_size / 2 - centroid), canvas_size - subject_size)))
    return offset[0], offset[1]


def save_cutout(canvas: Image.Image, destination: Path, icc: bytes | None) -> None:
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".png", delete=False) as file:
        temporary_path = Path(file.name)
    try:
        canvas.save(temporary_path, format="PNG", icc_profile=icc)
        os.replace(temporary_path, destination)
    finally:
        temporary_path.unlink(missing_ok=True)


def normalize_cutouts(
    source_dir: Path, out_dir: Path, canvas_size: tuple[int, int], fill_ratio: float
) -> dict:
    if source_dir.resolve() == out_dir.resolve():
        raise ValueError("--out must be a different directory from the input")
    sources = sorted(
        path for path in source_dir.iterdir()
        if path.is_file() and path.name.upper().startswith("SP_")
        and path.name.upper().endswith("_CUTOUT.PNG")
    )
    if not sources:
        raise ValueError(f"{source_dir}: no SP_*_CUTOUT.png files")

    canvas_w, canvas_h = canvas_size
    requested_height = max(1, round(canvas_h * fill_ratio))
    shared_height = requested_height
    for path in sources:
        cutout, _ = read_cutout(path)
        shared_height = min(shared_height, max(1, canvas_w * cutout.height // cutout.width))

    out_dir.mkdir(parents=True, exist_ok=True)
    for path in sources:
        cutout, icc = read_cutout(path)
        scale = min(shared_height / cutout.height, canvas_w / cutout.width)
        size = (max(1, round(cutout.width * scale)), max(1, round(cutout.height * scale)))
        resized = cutout.resize(size, Image.Resampling.LANCZOS)
        alpha = resized.getchannel("A")
        if not alpha.getbbox():
            raise ValueError(f"{path.name}: alpha vanished at the requested output size")
        canvas = Image.new("RGBA", canvas_size)
        canvas.paste(resized, optical_offset(alpha, canvas_size))
        save_cutout(canvas, out_dir / path.name, icc)

    return {
        "status": "PASS",
        "files_written": len(sources),
        "requested_subject_height_px": requested_height,
        "shared_subject_height_px": shared_height,
    }


def read_retouch_png(path: Path) -> tuple[Image.Image, bytes | None]:
    with path.open("rb") as handle:
        header = handle.read(25)
        handle.seek(0)
        with Image.open(handle) as image:
            if image.format != "PNG" or len(header) != 25 or header[24] != 8:
                raise ValueError(f"{path.name}: expected an 8-bit PNG")
            if getattr(image, "is_animated", False) or image.getexif().get(274, 1) != 1:
                raise ValueError(f"{path.name}: export a single frame with orientation applied")
            return image.convert("RGBA"), image.info.get("icc_profile")


def check_srgb(icc: bytes | None) -> dict:
    if not icc:
        return {"ok": False, "reason": "missing embedded ICC profile"}
    try:
        profile = ImageCms.ImageCmsProfile(BytesIO(icc))
        description = ImageCms.getProfileDescription(profile).strip()
        if profile.profile.xcolor_space.strip() != "RGB":
            return {"ok": False, "description": description, "reason": "ICC is not RGB"}

        # Compare the actual color transform, since sRGB profiles have several names.
        colors = np.array(list(product((0, 8, 16, 32, 64, 128, 192, 255), repeat=3)), dtype=np.uint8)
        patch = Image.fromarray(colors.reshape(16, 32, 3))
        converted = ImageCms.profileToProfile(
            patch, profile, SRGB, renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
            outputMode="RGB",
        )
        max_delta = int(np.abs(np.asarray(converted, dtype=np.int16) - np.asarray(patch)).max())
        return {"ok": max_delta <= 3, "description": description, "max_srgb_delta_8bit": max_delta}
    except (ImageCms.PyCMSError, OSError, ValueError):
        return {"ok": False, "reason": "unreadable embedded ICC profile"}


def detail_band(image: Image.Image) -> np.ndarray:
    rgb = np.asarray(image)[..., :3]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    horizontal = np.pad(luma, ((0, 0), (2, 2)), mode="edge")
    smooth_x = (
        horizontal[:, :-4] + 4 * horizontal[:, 1:-3] + 6 * horizontal[:, 2:-2]
        + 4 * horizontal[:, 3:-1] + horizontal[:, 4:]
    ) / 16
    vertical = np.pad(smooth_x, ((2, 2), (0, 0)), mode="edge")
    smooth_xy = (
        vertical[:-4] + 4 * vertical[1:-3] + 6 * vertical[2:-2]
        + 4 * vertical[3:-1] + vertical[4:]
    ) / 16
    return luma - smooth_xy


def mark_box(mask: np.ndarray, tile: Box, box: Box, value: bool) -> None:
    left, top = max(tile[0], box[0]), max(tile[1], box[1])
    right, bottom = min(tile[2], box[2]), min(tile[3], box[3])
    if left < right and top < bottom:
        mask[top - tile[1]:bottom - tile[1], left - tile[0]:right - tile[0]] = value


def measure_pores(
    before: Image.Image, after: Image.Image, eye_boxes: list[Box], skin_boxes: list[Box]
) -> tuple[float | None, int]:
    radius = DETAIL_RADIUS
    width, height = before.size
    regions = skin_boxes or [(0, 0, width, height)]
    left = min(box[0] for box in regions)
    right = max(box[2] for box in regions)
    top = min(box[1] for box in regions)
    bottom = max(box[3] for box in regions)

    reference_energy = error_energy = 0.0
    sampled_pixels = 0
    for y in range(top, bottom, 256):
        tile_bottom = min(y + 256, bottom)
        tile = (left, y, right, tile_bottom)
        samples = np.zeros((tile_bottom - y, right - left), dtype=bool)
        for box in regions:
            mark_box(samples, tile, box, True)
        for x0, y0, x1, y1 in eye_boxes:
            mark_box(samples, tile, (x0 - radius, y0 - radius, x1 + radius, y1 + radius), False)

        crop_x, crop_y = max(0, left - radius), max(0, y - radius)
        crop_box = (crop_x, crop_y, min(width, right + radius), min(height, tile_bottom + radius))
        tile_rows = slice(y - crop_y, tile_bottom - crop_y)
        tile_cols = slice(left - crop_x, right - crop_x)
        before_tile, after_tile = before.crop(crop_box), after.crop(crop_box)
        opaque_neighbors = ImageFilter.MinFilter(2 * radius + 1)
        before_alpha = before_tile.getchannel("A").filter(opaque_neighbors)
        samples &= np.asarray(before_alpha)[tile_rows, tile_cols] == 255
        if not samples.any():
            continue

        original = detail_band(before_tile)[tile_rows, tile_cols][samples]
        result = detail_band(after_tile)[tile_rows, tile_cols][samples]
        after_alpha = after_tile.getchannel("A").filter(opaque_neighbors)
        result[np.asarray(after_alpha)[tile_rows, tile_cols][samples] != 255] = 0
        reference_energy += float(np.sum(np.square(original), dtype=np.float64))
        error_energy += float(np.sum(np.square(result - original), dtype=np.float64))
        sampled_pixels += original.size

    if sampled_pixels == 0 or reference_energy / sampled_pixels < 0.25:
        return None, sampled_pixels  # Below 0.5 code values RMS, too little detail to score.
    retention = 100 * max(0.0, 1 - (error_energy / reference_energy) ** 0.5)
    return retention, sampled_pixels


def verify_retouch(before_path: Path, after_path: Path, eye_boxes: list[Box], skin_boxes: list[Box]) -> dict:
    before, before_icc = read_retouch_png(before_path)
    after, after_icc = read_retouch_png(after_path)
    if before.size != after.size:
        raise ValueError("before and after must have the same dimensions and alignment")
    width, height = before.size
    if any(box[2] > width or box[3] > height for box in eye_boxes + skin_boxes):
        raise ValueError("eye and skin boxes must be entirely inside both images")

    eyes = []
    for box in eye_boxes:
        delta = np.abs(np.asarray(before.crop(box), dtype=np.int16) - np.asarray(after.crop(box)))
        changed = int(np.count_nonzero(np.any(delta, axis=2)))
        eyes.append({
            "box_xywh": [box[0], box[1], box[2] - box[0], box[3] - box[1]],
            "changed_pixels": changed,
            "max_delta_8bit": int(delta.max()),
            "ok": changed == 0,
        })
    pores, sampled_pixels = measure_pores(before, after, eye_boxes, skin_boxes)
    icc = {"before": check_srgb(before_icc), "after": check_srgb(after_icc)}
    passes = all(item["ok"] for item in eyes) and all(item["ok"] for item in icc.values())
    passes = passes and pores is not None and pores >= MIN_PORE_RETENTION
    return {
        "status": "PASS" if passes else "FAIL",
        "eye_socket_guard": eyes,
        "pore_retention_pct": round(pores, 3) if pores is not None else None,
        "pore_retention_min_pct": MIN_PORE_RETENTION,
        "pore_sample_scope": "skin_boxes" if skin_boxes else "frame_excluding_eye_boxes",
        "pore_sample_pixels": sampled_pixels,
        "icc_srgb": icc,
    }


def self_test() -> None:
    def run_cli(*arguments: str, expected_exit: int = 0) -> dict:
        stdout = StringIO()
        with redirect_stdout(stdout):
            code = main(list(arguments))
        if code != expected_exit:
            raise AssertionError(f"unexpected exit {code}: {stdout.getvalue()}")
        return json.loads(stdout.getvalue())

    icc = ImageCms.ImageCmsProfile(SRGB).tobytes()
    with tempfile.TemporaryDirectory(prefix="ps2026-studio-") as directory:
        root = Path(directory)
        source, out = root / "input", root / "out"
        source.mkdir()
        for name, boxes in (
            ("A", [(15, 10, 40, 60)]),
            ("B", [(3, 23, 27, 63), (27, 48, 35, 63)]),
        ):
            asset = Image.new("RGBA", (100, 90))
            for box in boxes:
                asset.paste((160, 80, 40, 255), box)
            asset.save(source / f"SP_{name}_CUTOUT.png", icc_profile=icc)
        normalize_args = ("--normalize-cutouts", str(source), "--out", str(out),
                          "--canvas", "1200x1200", "--fill-ratio", "0.78")
        batch = run_cli(*normalize_args)
        assert batch["files_written"] == 2 and batch["shared_subject_height_px"] == 936
        for path in sorted(out.glob("*.png")):
            with Image.open(path) as asset:
                alpha = asset.getchannel("A")
                _, y0, _, y1 = alpha.getbbox()
                assert asset.size == (1200, 1200) and y1 - y0 == 936
                assert asset.info.get("icc_profile") == icc
                coverage = np.asarray(alpha)
                for axis in (0, 1):
                    center = np.average(np.arange(1200) + 0.5, weights=coverage.sum(axis=axis))
                    assert abs(center - 600) <= 0.5

        # A wide cutout reduces the common height, including on a rerun.
        asset = Image.new("RGBA", (80, 20))
        asset.paste((20, 30, 40, 255), (2, 2, 78, 17))
        asset.save(source / "SP_WIDE_CUTOUT.png")
        batch = run_cli(*normalize_args)
        assert batch["shared_subject_height_px"] == 236 and batch["files_written"] == 3
        print("normalize-cutouts PASS")

        rng = np.random.default_rng(2026)
        texture = rng.integers(-16, 17, size=(72, 96, 1), dtype=np.int16)
        rgb = (np.array([146, 112, 98]) + texture).astype(np.uint8)
        before = Image.fromarray(rgb).convert("RGBA")
        before_path, after_path = root / "before.png", root / "after.png"
        before.save(before_path, icc_profile=icc)
        verify_args = (
            "--verify-retouch", str(before_path), str(after_path), "--eye-box", "15,12,66,16",
            "--skin-box", "20,35,54,30",
        )
        after = before.point(lambda value: min(255, value + 5))
        after.paste(before.crop((15, 12, 81, 28)), (15, 12))
        after.save(after_path, icc_profile=icc)
        report = run_cli(*verify_args)
        assert report["status"] == "PASS" and report["pore_retention_pct"] >= 92

        after.putpixel((16, 12), (255, 0, 0, 255))
        after.save(after_path, icc_profile=icc)
        report = run_cli(*verify_args, expected_exit=1)
        assert report["eye_socket_guard"][0]["changed_pixels"] == 1

        after = before.filter(ImageFilter.GaussianBlur(2))
        after.paste(before.crop((15, 12, 81, 28)), (15, 12))
        after.save(after_path, icc_profile=icc)
        report = run_cli(*verify_args, expected_exit=1)
        assert report["eye_socket_guard"][0]["ok"] and report["pore_retention_pct"] < 92

        after = before.copy()
        after.paste((0, 0, 0, 0), (30, 35, 74, 65))
        after.save(after_path, icc_profile=icc)
        report = run_cli(*verify_args, expected_exit=1)
        assert report["eye_socket_guard"][0]["ok"] and report["pore_retention_pct"] < 92

        before.save(after_path)
        report = run_cli(*verify_args, expected_exit=1)
        assert not report["icc_srgb"]["after"]["ok"]

        lab_icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("LAB")).tobytes()
        before.save(after_path, icc_profile=lab_icc)
        report = run_cli(*verify_args, expected_exit=1)
        assert not report["icc_srgb"]["after"]["ok"]
        print("verify-retouch PASS")
    print("SELF_TEST_OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--normalize-cutouts", type=Path, metavar="INPUT_DIR")
    mode.add_argument("--verify-retouch", type=Path, nargs=2, metavar=("BEFORE_PNG", "AFTER_PNG"))
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path, metavar="OUT_DIR", help="output directory for cutouts")
    parser.add_argument("--canvas", type=parse_canvas, default=(1200, 1200), metavar="WIDTHxHEIGHT")
    parser.add_argument("--fill-ratio", type=parse_fill_ratio, default=0.78)
    parser.add_argument("--eye-box", type=parse_box, action="append", metavar="X,Y,W,H",
                        help="complete protected eye region in pixels, repeatable")
    parser.add_argument("--skin-box", type=parse_box, action="append", metavar="X,Y,W,H",
                        help="skin region for pore measurement, repeatable")
    args = parser.parse_args(argv)

    try:
        if args.normalize_cutouts:
            if args.out is None:
                parser.error("--normalize-cutouts requires --out")
            if args.eye_box or args.skin_box:
                parser.error("--eye-box and --skin-box require --verify-retouch")
            report = normalize_cutouts(args.normalize_cutouts, args.out, args.canvas, args.fill_ratio)
        elif args.verify_retouch:
            if not args.eye_box or args.out is not None:
                parser.error("--verify-retouch requires --eye-box and takes no --out")
            report = verify_retouch(*args.verify_retouch, args.eye_box, args.skin_box or [])
        else:
            if args.out is not None or args.eye_box or args.skin_box:
                parser.error("--self-test creates its own inputs and outputs")
            self_test()
            return 0
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
