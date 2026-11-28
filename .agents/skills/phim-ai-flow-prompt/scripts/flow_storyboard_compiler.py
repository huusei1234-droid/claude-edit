#!/usr/bin/env python3
"""Kiểm tra storyboard V6 và xuất hai batch video độc lập."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import sys
from tempfile import NamedTemporaryFile
from unicodedata import normalize


IMAGE_BLOCK = "IMAGE XUẤT HIỆN"
SPACE_BLOCK = "CHỐT KHÔNG GIAN & VỊ TRÍ"
PROMPT_BLOCK = "BẮT ĐẦU PROMPT"
REQUIRED_BLOCKS = (IMAGE_BLOCK, SPACE_BLOCK, PROMPT_BLOCK)

PACKSHOT_WORDS = re.compile(r"\b(?:hộp|lọ|chai|gói|túi quà|sản phẩm|nhãn)\b")
PACKSHOT_REF = re.compile(r"(?:SKU_REF(?:[-_][A-Z0-9]+[A-Z0-9_-]*)?|SP_[A-Z0-9]+[A-Z0-9_-]*)")
PACKSHOT_LOCK = "mặt bàn trống gọn gàng, tuyệt đối không có hộp giấy hay túi quà"

SCENE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
CHARACTER_ID = re.compile(r"CH-[A-Z0-9]+[A-Z0-9_-]*")
SHOT_SIZES = {"EWS", "WS", "MLS", "MS", "MCU", "CU", "ECU"}
WIDE_SHOT_SIZES = {"WS", "MLS"}
SCREEN_SIDES = {
    "left": "bên trái khung hình",
    "center": "giữa khung hình",
    "right": "bên phải khung hình",
    "offscreen": "ngoài khung hình",
}

SYLLABLES_PER_SECOND = 3.8
MAX_SECONDS = 15


@dataclass(frozen=True)
class Position:
    side: str
    place: str


@dataclass(frozen=True)
class Scene:
    id: str
    label: str
    setting: str
    camera_axis: str
    shot_size: str
    blocks: dict[str, str]
    refs: list[dict[str, str]]
    start_positions: dict[str, Position]
    end_positions: dict[str, Position]
    dialogue: list[tuple[str, str]]
    optimal_seconds: int


def text_field(value: object) -> str:
    return normalize("NFC", value.strip()) if isinstance(value, str) else ""


def comparable_text(value: str) -> str:
    return " ".join(normalize("NFC", value).casefold().split())


def read_refs(value: object, label: str, errors: list[str]) -> list[dict[str, str]]:
    if not isinstance(value, list):
        errors.append(f"{label}: refs phải là một mảng.")
        return []

    refs = []
    seen = set()
    for index, entry in enumerate(value, 1):
        ref_label = f"{label}, refs[{index}]"
        ref_id = text_field(entry.get("id") if isinstance(entry, dict) else entry).upper()
        if not SCENE_ID.fullmatch(ref_id):
            errors.append(f"{ref_label}: cần một mã tham chiếu hợp lệ.")
            continue
        if ref_id in seen:
            errors.append(f"{ref_label}: mã {ref_id} bị trùng.")
            continue
        seen.add(ref_id)
        ref = {"id": ref_id}
        if isinstance(entry, dict):
            path = text_field(entry.get("path"))
            if not path or "\x00" in path:
                errors.append(f"{ref_label}: cần path tệp ảnh hợp lệ.")
                continue
            ref["path"] = path
            if name := text_field(entry.get("name")):
                ref["name"] = name
        refs.append(ref)
    return refs


def read_positions(
    value: object, label: str, errors: list[str]
) -> dict[str, Position]:
    if not isinstance(value, dict):
        errors.append(f"{label}: cần một object vị trí theo mã nhân vật.")
        return {}

    positions = {}
    for character, entry in value.items():
        if not CHARACTER_ID.fullmatch(character):
            errors.append(f"{label}: mã nhân vật {character!r} phải có dạng CH-1.")
            continue
        if not isinstance(entry, dict):
            errors.append(f"{label}: thiếu vị trí có side và place cho {character}.")
            continue
        side = text_field(entry.get("side")).lower()
        place = text_field(entry.get("place"))
        if side not in SCREEN_SIDES or not place:
            errors.append(
                f"{label}: vị trí của {character} cần side "
                "left/center/right/offscreen và mô tả place."
            )
            continue
        positions[character] = Position(side, place)
    return positions


def read_dialogue(
    value: object, label: str, errors: list[str]
) -> list[tuple[str, str]]:
    if not isinstance(value, list):
        errors.append(f"{label}: dialogue phải là một mảng, dùng [] cho cảnh không thoại.")
        return []

    dialogue = []
    for index, entry in enumerate(value, 1):
        speaker = text_field(entry.get("speaker")) if isinstance(entry, dict) else ""
        line = text_field(entry.get("text")) if isinstance(entry, dict) else ""
        if not speaker or not line:
            errors.append(f"{label}: mục dialogue[{index}] cần speaker và text.")
            continue
        dialogue.append((speaker, line))
    return dialogue


def estimate_seconds(
    dialogue: list[tuple[str, str]], action_seconds: object, label: str, errors: list[str]
) -> int:
    if type(action_seconds) not in (int, float) or not 0 <= action_seconds <= MAX_SECONDS:
        errors.append(f"{label}: action_seconds phải là số từ 0 đến {MAX_SECONDS}.")
        return 0

    syllables = sum(len(re.findall(r"[^\W_]+", line)) for _, line in dialogue)
    duration = max(1, math.ceil(syllables / SYLLABLES_PER_SECOND + action_seconds))
    if duration > MAX_SECONDS:
        errors.append(
            f"{label}: cần {duration} giây ({syllables} âm tiết + "
            f"{action_seconds:g} giây hành động), vượt {MAX_SECONDS} giây. "
            "Hãy chia thành các cảnh nối tiếp hoặc điều chỉnh hành động."
        )
    return duration


def has_packshot_ref(refs: list[dict[str, str]]) -> bool:
    return any(PACKSHOT_REF.fullmatch(ref["id"]) for ref in refs)


def anti_fake_packshot_check(scene: Scene) -> list[str]:
    if has_packshot_ref(scene.refs):
        return []
    authored_text = [
        *scene.blocks.values(),
        *(part for line in scene.dialogue for part in line),
        *(position.place for position in scene.start_positions.values()),
        *(position.place for position in scene.end_positions.values()),
    ]
    keywords = sorted({
        match
        for text in authored_text
        for match in PACKSHOT_WORDS.findall(comparable_text(text))
    })
    if not keywords:
        return []
    return [
        f"{scene.label}: chống hộp giả phát hiện {', '.join(keywords)}. "
        "Cần đính kèm ảnh thật trong refs bằng mã SKU_REF hoặc SP_<mã>."
    ]


def read_scene(raw: dict, index: int, errors: list[str]) -> Scene:
    scene_id = text_field(raw.get("id"))
    label = f"Cảnh {index} ({scene_id})" if scene_id else f"Cảnh {index}"
    if not SCENE_ID.fullmatch(scene_id):
        errors.append(f"{label}: id chỉ dùng chữ Latin, chữ số, gạch nối và gạch dưới.")

    blocks = {block: text_field(raw.get(block)) for block in REQUIRED_BLOCKS}
    for block, content in blocks.items():
        if not content:
            errors.append(f"{label}: thiếu nội dung khối {block}.")

    setting = text_field(raw.get("setting"))
    if not setting:
        errors.append(f"{label}: thiếu mã bối cảnh setting.")
    camera_axis = text_field(raw.get("camera_axis")).upper()
    if camera_axis not in {"A", "B"}:
        errors.append(f"{label}: camera_axis phải là A hoặc B theo cùng quy ước bối cảnh.")
    shot_size = text_field(raw.get("shot_size")).upper()
    if shot_size not in SHOT_SIZES:
        errors.append(f"{label}: shot_size phải là một trong {', '.join(sorted(SHOT_SIZES))}.")

    refs = read_refs(raw.get("refs"), label, errors)
    start = read_positions(raw.get("start_positions"), f"{label}, start_positions", errors)
    end = read_positions(raw.get("end_positions"), f"{label}, end_positions", errors)
    characters = {ref["id"] for ref in refs if CHARACTER_ID.fullmatch(ref["id"])}
    characters.update(start, end)
    for field, positions in (("start_positions", start), ("end_positions", end)):
        for character in sorted(characters - positions.keys()):
            errors.append(f"{label}: thiếu vị trí {character} trong {field}.")

    dialogue = read_dialogue(raw.get("dialogue"), label, errors)
    seconds = estimate_seconds(dialogue, raw.get("action_seconds"), label, errors)
    return Scene(
        scene_id, label, setting, camera_axis, shot_size, blocks, refs, start, end,
        dialogue, seconds,
    )


def continuity_check(previous: Scene, following: Scene) -> list[str]:
    if not previous.setting or comparable_text(previous.setting) != comparable_text(following.setting):
        return []

    label = f"{previous.label} → {following.label}, bối cảnh {previous.setting}"
    errors = []
    end = previous.end_positions
    start = following.start_positions
    shared_characters = end.keys() & start.keys()
    side_changes = {(end[character].side, start[character].side) for character in shared_characters}

    if {previous.camera_axis, following.camera_axis} == {"A", "B"}:
        errors.append(
            f"{label}: nhảy trục 180° (camera_axis {previous.camera_axis} → "
            f"{following.camera_axis})."
        )
    elif {("left", "right"), ("right", "left")} <= side_changes:
        errors.append(f"{label}: nhảy trục 180° (hai nhân vật đảo trái/phải qua điểm cắt).")

    for character in sorted(start.keys() - end.keys()):
        errors.append(f"{label}: thiếu vị trí {character} trong end_positions của cảnh trước.")
    for character in sorted(end.keys() - start.keys()):
        errors.append(f"{label}: thiếu vị trí {character} trong start_positions của cảnh sau.")
    for character in sorted(shared_characters):
        before, after = end[character], start[character]
        if before.side != after.side or comparable_text(before.place) != comparable_text(after.place):
            errors.append(
                f"{label}: {character} lệch vị trí: "
                f"{before.side} ({before.place}) → {after.side} ({after.place})."
            )
    return errors


def validate_storyboard(document: object) -> tuple[list[Scene], list[str]]:
    entries = document.get("scenes") if isinstance(document, dict) else None
    if not isinstance(entries, list) or not entries:
        return [], ["Storyboard phải là một object có mảng scenes không rỗng."]

    scenes = []
    errors = []
    seen_ids = set()
    previous = None
    for index, raw in enumerate(entries, 1):
        if not isinstance(raw, dict):
            errors.append(f"Cảnh {index}: cần một object JSON.")
            previous = None
            continue
        scene = read_scene(raw, index, errors)
        if scene.id.casefold() in seen_ids:
            errors.append(f"{scene.label}: id cảnh bị trùng.")
        seen_ids.add(scene.id.casefold())
        errors.extend(anti_fake_packshot_check(scene))
        if previous is not None:
            errors.extend(continuity_check(previous, scene))
        scenes.append(scene)
        previous = scene

    total = len(entries)
    wide_count = sum(scene.shot_size in WIDE_SHOT_SIZES for scene in scenes)
    if not 25 * total <= 100 * wide_count <= 40 * total:
        errors.append(
            f"Tỷ lệ WS/MLS là {wide_count}/{total} ({wide_count / total:.1%}), "
            "yêu cầu từ 25% đến 40% tổng số cảnh."
        )
    return scenes, errors


def render_positions(positions: dict[str, Position]) -> str:
    return " | ".join(
        f"{character} {SCREEN_SIDES[position.side]}, {position.place}"
        for character, position in positions.items()
    ) or "Không có nhân vật."


def build_batch(
    scenes: list[Scene], ratio: str, destination: Path, storyboard_dir: Path
) -> list[dict]:
    width, height = (1080, 1920) if ratio == "9:16" else (1920, 1080)
    framing = (
        "Bố cục dọc giữ mặt và hành động chính trong khung."
        if ratio == "9:16"
        else "Bố cục ngang khai thác chiều rộng bối cảnh."
    )
    jobs = []
    for scene in scenes:
        job_id = f"{scene.id}_{ratio.replace(':', 'x')}"
        lines = [
            IMAGE_BLOCK,
            scene.blocks[IMAGE_BLOCK],
            "",
            SPACE_BLOCK,
            scene.blocks[SPACE_BLOCK],
            f"Trục máy {scene.camera_axis}.",
            f"Đầu cảnh — {render_positions(scene.start_positions)}",
            f"Cuối cảnh — {render_positions(scene.end_positions)}",
            "",
            PROMPT_BLOCK,
            f"Tạo video {scene.optimal_seconds} giây, tỷ lệ {ratio}, "
            f"photorealistic live-action, cỡ cảnh {scene.shot_size}. {framing}",
            scene.blocks[PROMPT_BLOCK],
        ]
        if scene.dialogue:
            lines.append("THOẠI")
            lines.extend(f"{speaker} — “{line}”" for speaker, line in scene.dialogue)
        if not has_packshot_ref(scene.refs):
            lines.append(PACKSHOT_LOCK)

        refs = []
        for source in scene.refs:
            ref = source.copy()
            if "path" in ref:
                asset = (storyboard_dir / ref["path"]).resolve()
                ref["path"] = str(asset)
                ref.setdefault("name", asset.name)
            refs.append(ref)
        jobs.append({
            "id": job_id,
            "scene": scene.id,
            "ratio": ratio,
            "size": ratio,
            "width": width,
            "height": height,
            "seconds": scene.optimal_seconds,
            "optimal_seconds": scene.optimal_seconds,
            "prompt": "\n".join(lines),
            "refs": refs,
            "outPath": str(destination / f"{job_id}.mp4"),
        })
    return jobs


def write_batches(batches: dict[Path, list[dict]]) -> None:
    # Chuẩn bị cả hai tệp trước khi thay thế từng batch.
    staged = {}
    try:
        for path, jobs in batches.items():
            if path.exists() and not path.is_file():
                raise OSError(f"Đường dẫn batch không phải tệp: {path}")
            path.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
            ) as temporary:
                staged[path] = Path(temporary.name)
                json.dump(jobs, temporary, ensure_ascii=False, indent=2)
                temporary.write("\n")
        for path, temporary in staged.items():
            temporary.replace(path)
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def report_errors(errors: list[str]) -> int:
    red, reset = ("\x1b[31m", "\x1b[0m") if sys.stderr.isatty() else ("", "")
    for error in errors:
        print(f"{red}LỖI: {error}{reset}", file=sys.stderr)
    print(f"Kiểm tra thất bại: {len(errors)} lỗi.", file=sys.stderr)
    return 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Tệp storyboard JSON UTF-8.")
    parser.add_argument("--validate", action="store_true", help="Kiểm tra storyboard.")
    parser.add_argument("--compile-out", type=Path, metavar="BATCH.JSON",
                        help="Ghi batch dọc tại đây, batch ngang trong thư mục con Ngang.")
    args = parser.parse_args()
    if not (args.validate or args.compile_out):
        parser.error("cần --validate, --compile-out hoặc cả hai.")

    try:
        source = args.input.resolve()
        document = json.loads(source.read_text(encoding="utf-8-sig"))
        scenes, errors = validate_storyboard(document)
        if errors:
            return report_errors(errors)
        if args.compile_out:
            vertical = args.compile_out.absolute()
            horizontal = vertical.parent / "Ngang" / vertical.name
            resolved_outputs = {vertical.resolve(), horizontal.resolve()}
            if source in resolved_outputs or len(resolved_outputs) != 2:
                return report_errors(["Hai đường dẫn batch phải riêng biệt và khác storyboard nguồn."])
            write_batches({
                vertical: build_batch(scenes, "9:16", vertical.parent, source.parent),
                horizontal: build_batch(scenes, "16:9", horizontal.parent, source.parent),
            })
    except json.JSONDecodeError as error:
        return report_errors([f"JSON sai cú pháp ở dòng {error.lineno}, cột {error.colno}: {error.msg}"])
    except (OSError, UnicodeError, ValueError) as error:
        return report_errors([str(error)])

    wide_count = sum(scene.shot_size in WIDE_SHOT_SIZES for scene in scenes)
    print(f"Kiểm tra đạt: {len(scenes)} cảnh, WS/MLS {wide_count}/{len(scenes)}, 0 lỗi.")
    if args.compile_out:
        print(f"Batch dọc 9:16: {vertical}")
        print(f"Batch ngang 16:9: {horizontal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
