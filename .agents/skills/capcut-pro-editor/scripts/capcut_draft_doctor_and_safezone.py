"""Audit and upgrade a copy of a CapCut Desktop draft with Python 3.11."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import tempfile
import uuid
from collections import defaultdict
from collections.abc import Iterator
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from urllib.parse import urlsplit
from urllib.request import url2pathname


Y_MIN, Y_MAX = -0.58, 0.72
LOWER_Y, LOWER_X = 0.10, -0.12
TOP, BOTTOM, LEFT, RIGHT = 248, 1548, 54, 1024
BUTTON_TOP, BUTTON_LEFT = 860, 884
HALF_WIDTH, HALF_HEIGHT = 540, 960
FADE_US, MIN_ZOOM_US = 40_000, 2_200_000

TEXT_TYPES = {"text", "texts", "subtitle", "subtitles", "text_template", "text_templates"}
STICKER_TYPES = {"sticker", "stickers"}
AUDIO_TYPES = {"audio", "audios"}
VIDEO_TYPES = {"video", "videos"}
IMAGE_TYPES = {"image", "images", "photo", "photos"}
MEDIA_TYPES = AUDIO_TYPES | VIDEO_TYPES | IMAGE_TYPES | STICKER_TYPES
MEDIA_PATH_FIELDS = (
    "path", "local_path", "file_path", "source_path", "media_path", "original_path",
    "proxy_path", "reverse_path", "video_path", "audio_path", "image_path",
    "intensifies_audio_path", "intensifies_path", "reverse_intensifies_path",
)
SPEECH = re.compile(r"(?<!\w)(vo|voice\s*over|voice|dialogue|speech|narration|tts|thoại|giọng)(?!\w)")
NON_SPEECH = re.compile(r"(?<!\w)(bgm|music|sfx|ambience|ambient|sound effects?|nhạc|hiệu ứng)(?!\w)")
TRANSFORM_KEYS = ("kftypeposition", "kftypescale", "kftyperot", "kftypetransform")


def records(value: object) -> Iterator[dict]:
    if isinstance(value, list):
        yield from (item for item in value if isinstance(item, dict))


def obj(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def number(value: object, default: float = 0.0) -> float:
    if type(value) is int or (type(value) is float and math.isfinite(value)):
        return value
    return default


def clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def new_id() -> str:
    return str(uuid.uuid4()).upper()


def material_rows(draft: dict) -> Iterator[tuple[str, dict]]:
    for bucket, items in draft["materials"].items():
        for item in records(items):
            yield bucket.casefold(), item


def segment_rows(draft: dict) -> Iterator[tuple[dict, dict]]:
    for track in records(draft.get("tracks")):
        for segment in records(track.get("segments")):
            yield track, segment


def material_index(draft: dict) -> dict:
    return {item["id"]: (bucket, item) for bucket, item in material_rows(draft)
            if isinstance(item.get("id"), str) and item["id"]}


def kind(item: dict) -> str:
    return str(item.get("type", "")).casefold()


def overlay_types(types: set[str]) -> bool:
    return bool(types & (TEXT_TYPES | STICKER_TYPES))


def placement(item: dict) -> dict | None:
    """Find the object owning transform and scale in native and older drafts."""
    clip = obj(item.get("clip"))
    if isinstance(clip.get("transform"), dict):
        return clip
    if isinstance(item.get("transform"), dict):
        return item
    return None


def overlay_rows(draft: dict) -> Iterator[tuple[str, dict, dict | None, dict]]:
    materials = material_index(draft)
    for bucket, item in material_rows(draft):
        if overlay_types({bucket, kind(item)}):
            owner = placement(item)
            if owner is not None:
                yield f"material {item.get('id', '?')}", item, owner, item
    for track, segment in segment_rows(draft):
        bucket, material = materials.get(segment.get("material_id"), ("", {}))
        if not overlay_types({bucket, kind(material), kind(segment), kind(track)}):
            continue
        owner = placement(segment)
        if owner is None and placement(material) is not None:
            continue  # This segment uses the material placement already visited above.
        yield f"segment {segment.get('id', '?')}", segment, owner, material


def scale_xy(owner: dict) -> tuple[float, float]:
    scale = owner.get("scale", 1.0)
    if isinstance(scale, dict):
        return number(scale.get("x"), 1.0), number(scale.get("y"), 1.0)
    uniform = number(scale, 1.0)
    return uniform, uniform


def pixel_size(axis: str, *sources: dict) -> float | None:
    for source in sources:
        value = number(source.get(axis))
        if value >= 1:
            return value
    return None


def projected_size(item: dict, owner: dict, material: dict) -> tuple[float | None, float | None]:
    width = pixel_size("width", owner, item, material)
    height = pixel_size("height", owner, item, material)
    sx, sy = scale_xy(owner)
    width = None if width is None else width * abs(sx)
    height = None if height is None else height * abs(sy)
    rotation = math.radians(number(owner.get("rotation")) % 360)
    sin, cos = abs(math.sin(rotation)), abs(math.cos(rotation))
    if sin < 1e-9:
        return width, height
    if cos < 1e-9:
        return height, width
    if width is None or height is None:
        return None, None
    return width * cos + height * sin, width * sin + height * cos


def center_y(y: float, height: float) -> float:
    return clamp(HALF_HEIGHT * (1 - y), TOP + height / 2, BOTTOM - height / 2)


def safe_geometry(x: float, y: float, width: float, height: float) -> tuple[float, float, float]:
    y = clamp(y, Y_MIN, Y_MAX)
    usable_height = min(height, BOTTOM - TOP)
    bottom_edge = center_y(y, usable_height) + usable_height / 2
    lower = y <= LOWER_Y or bottom_edge >= BUTTON_TOP - 1e-7
    right = BUTTON_LEFT if lower else RIGHT
    preferred_center = HALF_WIDTH * (1 + (LOWER_X if lower else x))
    max_width = 2 * min(preferred_center - LEFT, right - preferred_center) if lower else right - LEFT
    shrink = min(1.0, max_width / width if width else 1.0, (BOTTOM - TOP) / height if height else 1.0)
    if 1 - shrink < 1e-10:
        shrink = 1.0
    half_width = width * shrink / 2
    safe_x = clamp(preferred_center, LEFT + half_width, right - half_width)
    safe_y = center_y(y, height * shrink)
    return round(safe_x / HALF_WIDTH - 1, 10), round(1 - safe_y / HALF_HEIGHT, 10), shrink


def has_transform_keys(item: dict) -> bool:
    return bool(item.get("keyframe_refs") or item.get("keyframes")) or any(
        str(group.get("property_type", "")).casefold().startswith(TRANSFORM_KEYS)
        for group in records(item.get("common_keyframes"))
    )


def animated_material_ids(draft: dict) -> set[str]:
    return {item["id"] for item in records(draft["materials"].get("material_animations"))
            if isinstance(item.get("id"), str) and item.get("animations")}


def has_resource_animation(item: dict, animated_ids: set[str]) -> bool:
    return any(ref in animated_ids for ref in (item.get("extra_material_refs") or []))


def audit_safe_zone(draft: dict, *, fix: bool = False, report: bool = True) -> dict[str, int]:
    canvas = obj(draft.get("canvas_config"))
    if (canvas.get("width"), canvas.get("height")) != (1080, 1920):
        raise ValueError("Vùng an toàn V6 yêu cầu canvas_config 1080×1920.")

    counts = dict(scanned=0, issues=0, fixed=0, unknown_bounds=0, animated=0)
    animated_ids = animated_material_ids(draft)
    for label, item, owner, material in overlay_rows(draft):
        counts["scanned"] += 1
        layout = owner if owner is not None else obj(item.get("clip"))
        transform = obj(layout.get("transform"))
        x, y = number(transform.get("x")), number(transform.get("y"))
        width, height = projected_size(item, layout, material)
        new_x, new_y, shrink = safe_geometry(x, y, width or 0.0, height or 0.0)
        needs_fix = abs(new_x - x) > 1e-9 or abs(new_y - y) > 1e-9 or shrink < 1.0
        unknown = width is None or height is None
        animated = has_transform_keys(item) or has_resource_animation(item, animated_ids)
        if unknown:
            counts["unknown_bounds"] += 1
        if animated:
            counts["animated"] += 1
        if needs_fix:
            counts["issues"] += 1
            if fix:
                if owner is None:
                    owner = item.get("clip")
                    if not isinstance(owner, dict):
                        owner = item["clip"] = {}
                    transform = owner["transform"] = {}
                transform.update(x=new_x, y=new_y)
                if shrink < 1.0:
                    sx, sy = scale_xy(owner)
                    if isinstance(owner.get("scale"), dict):
                        owner["scale"].update(x=sx * shrink, y=sy * shrink)
                    elif isinstance(owner.get("scale"), (int, float)):
                        owner["scale"] = sx * shrink
                    else:
                        owner["scale"] = {"x": sx * shrink, "y": sy * shrink}
                counts["fixed"] += 1
        if report and (needs_fix or unknown or animated):
            details = []
            if needs_fix:
                details.append(f"({x:g}, {y:g}) → ({new_x:g}, {new_y:g}), hệ số giữ scale {shrink:.4f}")
            if unknown:
                details.append("thiếu kích thước pixel để kiểm tra toàn bộ mép")
            if animated:
                details.append("có chuyển động, cần kiểm tra mép theo thời gian")
            print(f"  {label} | " + " | ".join(details))
    if report:
        print(
            f"SAFE_ZONE scanned={counts['scanned']} issues={counts['issues']} fixed={counts['fixed']} "
            f"unknown_bounds={counts['unknown_bounds']} animated={counts['animated']}"
        )
    return counts


def duration_us(segment: dict) -> int:
    return int(number(obj(segment.get("target_timerange")).get("duration")))


def make_zoom(duration: int) -> dict:
    points = []
    for step in range(5):
        t = step / 4
        smoothstep = t * t * (3 - 2 * t)
        points.append({
            "id": new_id(), "curveType": "Line", "time_offset": round(duration * t),
            "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
            "values": [1.0 + 0.06 * smoothstep], "string_value": "", "graphID": "",
        })
    return {"id": new_id(), "material_id": "", "property_type": "KFTypeScale", "keyframe_list": points}


def speech_cut(segment: dict, track: dict, material: dict, bucket: str, duration: int) -> bool:
    track_type = kind(track)
    if track_type not in AUDIO_TYPES | VIDEO_TYPES or duration <= 0:
        return False
    labels = [
        str(item.get(field) or "")
        for item in (segment, track, material)
        for field in ("name", "material_name", "track_name", "audio_role", "role", "category_name")
    ]
    labels.append(PureWindowsPath(str(material.get("path") or "")).stem)
    metadata = " ".join(labels).casefold().replace("_", " ")
    if number(segment.get("volume"), 1.0) <= 0 or material.get("has_audio") is False:
        return False
    if NON_SPEECH.search(metadata) or kind(material) in {"music", "sfx", "sound_effect"}:
        return False
    if SPEECH.search(metadata) or kind(material) in {"tts", "text_to_speech"}:
        return True
    # Match the existing short-cut convention for unlabeled audio, never for video sound.
    return track_type in AUDIO_TYPES and bucket not in VIDEO_TYPES | IMAGE_TYPES and 300_000 <= duration <= 12_000_000


def add_micro_fade(draft: dict, segment: dict, fades: dict, amount: int) -> bool:
    durations = {"fade_in_duration": amount, "fade_out_duration": amount}
    refs = segment.get("extra_material_refs") or []
    fade_refs = [ref for ref in refs if ref in fades]
    inline = segment.get("audio_fade")
    inline_changed = isinstance(inline, dict) and any(inline.get(key) != value for key, value in durations.items())
    if inline_changed:
        inline.update(durations)
    existing = fades[fade_refs[0]] if len(fade_refs) == 1 else {}
    if all(existing.get(key) == value for key, value in durations.items()):
        return inline_changed
    fade = {"id": new_id(), "type": "audio_fade", "fade_type": 0, **durations}
    fade_rows = draft["materials"].get("audio_fades")
    if not isinstance(fade_rows, list):
        fade_rows = draft["materials"]["audio_fades"] = []
    fade_rows.append(fade)
    fades[fade["id"]] = fade
    segment["extra_material_refs"] = [ref for ref in refs if ref not in fades] + [fade["id"]]
    return True


def inject_dna_motion(draft: dict) -> tuple[int, int]:
    materials = material_index(draft)
    fades = {item["id"]: item for item in records(draft["materials"].get("audio_fades"))
             if isinstance(item.get("id"), str)}
    animated_ids = animated_material_ids(draft)
    zoomed = faded = 0
    for track, segment in segment_rows(draft):
        bucket, material = materials.get(segment.get("material_id"), ("", {}))
        duration = duration_us(segment)
        owner = obj(segment.get("clip")) or segment
        is_video = kind(track) in VIDEO_TYPES and bucket in VIDEO_TYPES | {""}
        is_video &= not (kind(material) in (IMAGE_TYPES | STICKER_TYPES | TEXT_TYPES))
        is_video &= not (kind(segment) in (IMAGE_TYPES | STICKER_TYPES | TEXT_TYPES))
        if (is_video and duration > MIN_ZOOM_US and scale_xy(owner) == (1.0, 1.0)
                and not has_transform_keys(segment) and not has_resource_animation(segment, animated_ids)):
            segment["common_keyframes"] = list(records(segment.get("common_keyframes"))) + [make_zoom(duration)]
            zoomed += 1
        if speech_cut(segment, track, material, bucket, duration) and duration >= 2:
            faded += add_micro_fade(draft, segment, fades, min(FADE_US, duration // 2))
    return zoomed, faded


def local_media_path(raw: str, draft_dir: Path) -> tuple[Path, str] | None:
    # A Windows drive letter is not a URI scheme.
    if re.match(r"^[a-z][a-z\d+.-]*://", raw, re.IGNORECASE):
        uri = urlsplit(raw)
        if uri.scheme.casefold() != "file":
            return None
        prefix = f"//{uri.netloc}" if uri.netloc.casefold() not in {"", "localhost"} else ""
        raw = url2pathname(prefix + uri.path)
    basename = PureWindowsPath(raw).name
    if not basename:
        return None
    path = Path(raw.replace("\\", os.sep))
    return draft_dir / path, basename


def relink_media(draft: dict, search_dir: Path, draft_dir: Path, *, report: bool = True) -> tuple[int, int]:
    if not search_dir.is_dir():
        raise ValueError(f"Thư mục media không tồn tại: {search_dir}")
    media = [item for bucket, item in material_rows(draft) if bucket in MEDIA_TYPES or kind(item) in MEDIA_TYPES]
    media.extend(segment for track, segment in segment_rows(draft) if {kind(track), kind(segment)} & MEDIA_TYPES)
    missing = defaultdict(list)
    for item in media:
        for field in MEDIA_PATH_FIELDS:
            raw = item.get(field)
            if not isinstance(raw, str) or not raw.strip():
                continue
            source = local_media_path(raw, draft_dir)
            if source is not None and not source[0].is_file():
                missing[source[1].casefold()].append((item, field, raw))

    def raise_scan_error(error: OSError) -> None:
        raise error

    matches = defaultdict(list)
    if missing:
        for directory, _, files in os.walk(search_dir, onerror=raise_scan_error):
            for name in files:
                key = name.casefold()
                if key in missing:
                    candidate = Path(directory, name)
                    if candidate.is_file():
                        matches[key].append(candidate)

    changed = unresolved = 0
    for key, fields in missing.items():
        candidates = matches[key]
        for item, field, raw in fields:
            if len(candidates) == 1:
                item[field] = candidates[0].resolve().as_posix()
                changed += 1
            else:
                unresolved += 1
                if report:
                    reason = "thiếu nguồn" if not candidates else f"trùng basename ({len(candidates)} tệp)"
                    print(f"  {item.get('id', '?')}.{field} | {reason} | {raw}")
    return changed, unresolved


def write_new_draft(draft: dict, output: Path) -> None:
    """Publish a complete file without overwriting any existing draft."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         suffix=".json.tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(draft, stream, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
            stream.write("\n")
        if os.name == "nt":
            temporary.rename(output)  # Windows rename fails if the target exists.
        else:
            os.link(temporary, output)  # Atomically publish a new name on POSIX.
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def self_test() -> None:
    # Use a known local file to exercise the resolver without writing any fixtures.
    sample_source = Path(__file__).resolve()
    missing_source = f"__v6_missing_source__/{sample_source.name.upper()}"
    draft = {
        "canvas_config": {"width": 1080, "height": 1920},
        "materials": {
            "videos": [{"id": "v", "type": "video", "path": missing_source}],
            "texts": [{"id": "t", "width": 1080, "height": 100, "content": "Tiếng Việt"}],
            "stickers": [{"id": "s", "transform": {"x": 0.0, "y": 0.90}}],
            "audios": [{"id": "vo", "path": "__v6_missing_voice__.wav"}],
            "audio_fades": [{"id": "old", "type": "audio_fade", "fade_in_duration": 80_000}],
        },
        "tracks": [
            {"type": "text", "segments": [
                {"id": "caption", "material_id": "t", "clip": {"transform": {"x": 0.40, "y": -0.90}}},
            ]},
            {"type": "video", "segments": [
                {"material_id": "v", "target_timerange": {"start": 7_000_000, "duration": 2_500_000}},
                {"material_id": "v", "target_timerange": {"duration": MIN_ZOOM_US}},
                {"material_id": "v", "target_timerange": {"duration": 3_000_000},
                 "common_keyframes": [{"property_type": "KFTypeScaleX"}]},
            ]},
            {"type": "audio", "name": "Thoại", "segments": [
                {"material_id": "vo", "target_timerange": {"duration": 950_000},
                 "extra_material_refs": ["old", "other"]},
            ]},
            {"type": "audio", "name": "BGM", "segments": [
                {"material_id": "vo", "target_timerange": {"duration": 900_000}, "extra_material_refs": ["old"]},
            ]},
        ],
    }
    before = deepcopy(draft)
    assert audit_safe_zone(draft, report=False)["issues"] == 2 and draft == before
    assert audit_safe_zone(draft, fix=True, report=False)["fixed"] == 2
    caption = draft["tracks"][0]["segments"][0]["clip"]
    assert caption["transform"]["x"] == LOWER_X
    assert Y_MIN <= caption["transform"]["y"] <= Y_MAX
    assert HALF_HEIGHT * (1 - caption["transform"]["y"]) + 50 * caption["scale"]["y"] <= BOTTOM + 1e-7
    assert HALF_WIDTH * (1 + LOWER_X) + 540 * caption["scale"]["x"] <= BUTTON_LEFT + 1e-9
    assert draft["materials"]["stickers"][0]["transform"]["y"] == Y_MAX
    assert audit_safe_zone(draft, fix=True, report=False)["fixed"] == 0

    assert inject_dna_motion(draft) == (1, 1)
    first, boundary, animated = draft["tracks"][1]["segments"]
    zoom = first["common_keyframes"][0]
    assert zoom["property_type"] == "KFTypeScale"
    assert [(p["time_offset"], p["values"][0]) for p in zoom["keyframe_list"][::4]] == [(0, 1.0), (2_500_000, 1.06)]
    assert "common_keyframes" not in boundary and len(animated["common_keyframes"]) == 1
    fade = draft["materials"]["audio_fades"][-1]
    assert fade["fade_in_duration"] == fade["fade_out_duration"] == 40_000
    assert draft["tracks"][2]["segments"][0]["extra_material_refs"] == ["other", fade["id"]]
    assert draft["tracks"][3] == before["tracks"][3]
    assert inject_dna_motion(draft) == (0, 0)

    assert relink_media(draft, sample_source.parent, sample_source.parent, report=False) == (1, 1)
    assert draft["materials"]["videos"][0]["path"] == sample_source.as_posix()
    assert draft["materials"]["audios"] == before["materials"]["audios"]
    print("SELF_TEST_OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="CapCut Draft Doctor V6 Siêu Cấp")
    parser.add_argument("--draft", type=Path, metavar="draft_content.json", help="Tệp JSON nguồn")
    parser.add_argument("--audit", action="store_true", help="Báo cáo vùng an toàn trên nháp nguồn 1080×1920")
    parser.add_argument("--fix-safe-zone", action="store_true", help="Căn text, phụ đề và sticker vào vùng an toàn")
    parser.add_argument("--inject-dna-motion", action="store_true", help="Thêm micro-zoom và micro-fade thoại")
    parser.add_argument("--relink-media", type=Path, metavar="DIR", help="Tìm lại media thiếu theo basename")
    parser.add_argument("--out", type=Path, metavar="new_draft.json", help="Tệp mới, mặc định <tên nguồn>.v6.json")
    parser.add_argument("--self-test", action="store_true", help="Chạy kiểm thử trên nháp trong bộ nhớ")
    args = parser.parse_args()
    editing = args.fix_safe_zone or args.inject_dna_motion or args.relink_media is not None
    if args.self_test:
        if args.draft or args.audit or editing or args.out:
            parser.error("--self-test chạy độc lập với các chế độ đọc và sửa nháp.")
        self_test()
        return
    if args.draft is None or not (args.audit or editing):
        parser.error("Cần --draft và ít nhất một chế độ audit, sửa vùng an toàn, DNA motion hoặc relink.")
    if args.out is not None and not editing:
        parser.error("--out dùng với chế độ chỉnh sửa.")

    try:
        with args.draft.open(encoding="utf-8-sig") as stream:
            draft = json.load(stream)
        if not isinstance(draft, dict) or not isinstance(draft.get("tracks"), list):
            raise ValueError("Nháp CapCut phải là object JSON chứa tracks dạng mảng.")
        if not isinstance(draft.get("materials"), dict):
            raise ValueError("Nháp CapCut phải chứa materials dạng object.")
        if args.audit:
            audit_safe_zone(draft)
        if args.fix_safe_zone:
            audit_safe_zone(draft, fix=True)
        if args.inject_dna_motion:
            zoomed, faded = inject_dna_motion(draft)
            print(f"DNA_MOTION zoomed={zoomed} faded={faded}")
        if args.relink_media is not None:
            changed, unresolved = relink_media(draft, args.relink_media, args.draft.absolute().parent)
            print(f"RELINK_MEDIA changed={changed} unresolved={unresolved}")
        if editing:
            output = args.out or args.draft.with_suffix(".v6.json")
            if output.exists() or output.is_symlink():
                raise FileExistsError(f"Tệp đích đã tồn tại, hãy chọn tên mới: {output}")
            write_new_draft(draft, output)
            print(f"OUT {output.absolute()}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Lỗi: {error}\n")


if __name__ == "__main__":
    main()
