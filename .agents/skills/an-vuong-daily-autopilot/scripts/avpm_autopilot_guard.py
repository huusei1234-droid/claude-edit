#!/usr/bin/env python3
"""Chọn trang phục Chị Hậu và kiểm văn bản sản xuất AVPM."""

import argparse
import re
import sqlite3
import unicodedata
from contextlib import closing
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory


OUTFITS = (
    "Đời thường ở nhà — áo thun kem, quần linen nâu nhạt",
    "Công sở — sơ mi xanh nhạt, quần tây xám than",
    "Đi bộ — áo polo trắng, quần jogger xanh rêu",
    "Trà chiều — váy midi hoa nhí xanh, cardigan kem",
    "Lụa buổi tối — áo lụa xanh đêm, quần suông đen",
    "Áo dài cách tân — áo xanh ngọc dáng ngắn, quần lụa trắng",
    "Dạo phố — áo thun sọc xanh trắng, jeans ống đứng",
    "Công sở — blazer be, áo cổ tròn trắng, quần nâu cacao",
    "Thể thao trong nhà — áo tập tím nhạt, quần thể thao xám đậm",
    "Trà chiều — áo kiểu hồng đất, chân váy xếp ly màu cát",
    "Lụa buổi tối — áo cổ đổ màu mận, chân váy midi đen",
    "Áo dài cách tân — áo hồng phấn cổ tròn, quần lụa kem",
    "Đời thường cuối tuần — sơ mi linen trắng, quần xanh olive",
    "Công sở — áo dệt kim cổ polo xanh navy, chân váy chữ A xám",
    "Thể thao ngoài trời — áo khoác gió xanh bạc hà, quần jogger đen",
    "Trà chiều — đầm sơ mi cotton vàng bơ, thắt lưng nâu nhạt",
)
DEFAULT_STATE = Path(__file__).resolve().parents[1] / "AVPM_OUTFIT_STATE.sqlite3"
PRODUCTS = ("AV Protein", "Bojomi", "Curcumilk Phyto", "Collamela")

EFFECTS = re.compile(r"\b(?:sparkl(?:e[sd]?|ing|y)|glitter(?:s|ing|ed|y)?|bling(?:s|ing|ed)?|kim\s+tuyến|lấp\s+lánh)\b")
MEDICAL = re.compile(r"\b(?:chữa\s+khỏi\s+dứt\s+điểm|thuốc\s+đặc\s+trị)\b")
STICK = re.compile(r"\bgói[\s-]+(?:stick|bột)\b")
VISUAL_EXCLUSIONS = re.compile(
    r"(?:^\s*(?:[-+]\s+)?|\|\s*|:\s*)"
    r"(?:lời thoại|thoại|dialogue|voice[- ]?over|vo|caption|phụ đề|text)\s*:"
)

SCENE_HEADER = re.compile(
    r"^\s*(?:#{1,6}\s+)?(?:[-+]\s+|\d+[.)]\s+|\|\s*)?"
    r"(?:cảnh|scene|shot)\s*#?\s*\d+(?:[a-z])?\b"
)
DURATION_FIELD = re.compile(r"^(?:thời lượng(?:\s+cảnh)?|duration)\s*[:=]\s*")
SCENE_DURATION_FIELD = re.compile(r"^\s*thời lượng cảnh\s*[:=]")
NUMBER = r"\d+(?:[.,]\d+)?"
CLOCK = r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d+)?"
UNIT = r"(?:giây|seconds?|secs?|s)(?!\w)"
TIME_POINT = rf"(?:{CLOCK}|{NUMBER}(?:\s*{UNIT})?)"
TIME_RANGE = re.compile(rf"(?P<start>{TIME_POINT})(?:\s*[-–—→]\s*|\s+đến\s+)(?P<end>{TIME_POINT})(?![\w.,:])")
TIME_SECONDS = re.compile(rf"(?P<value>{NUMBER})\s*{UNIT}")
MIN_SECONDS = Decimal("1.8")
MAX_SECONDS = Decimal("2.7")

PREP_STEPS = {"open": "mở gói", "powder": "đổ bột", "water": "thêm nước", "mix": "khuấy/lắc"}
PREP = re.compile(
    r"(?P<open>\b(?:xé|mở|cắt)\s+(?:(?:mép|miệng|đầu)\s+)?(?:gói|stick)\b)"
    r"|(?P<powder>\b(?:đổ|cho|trút|dốc)\s+(?:(?:phần|toàn bộ|hết)\s+)*(?:bột|gói\s+bột|(?:gói\s+)?stick)\b)"
    rf"|(?P<water>\b(?:thêm|rót|đổ|cho|đong|chế)\s+(?:{NUMBER}\s*(?:ml|lít)\s+)?nước\b)"
    r"|(?P<mix>\b(?:khuấy|lắc\s+(?:đều|tan))\b)"
)
PREP_NEGATION = re.compile(r"\b(?:không|chưa|đừng|bỏ qua(?:\s+bước)?)\s+$")
PREP_ORDERS = {
    ("open", "powder", "water", "mix"),
    ("open", "water", "powder", "mix"),
    ("water", "open", "powder", "mix"),
}


@dataclass(frozen=True)
class Finding:
    level: str
    line: int | None
    message: str


@dataclass
class Scene:
    line: int
    seconds: Decimal | None


def next_outfit(state_file: Path) -> tuple[str, str]:
    """Giữ một vị trí xoay chung qua nhiều lần gọi CLI và tiến trình."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(state_file, timeout=10)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            "CREATE TABLE IF NOT EXISTS outfit_rotation "
            "(id INTEGER PRIMARY KEY CHECK (id = 1), next_index INTEGER NOT NULL)"
        )
        db.execute("INSERT OR IGNORE INTO outfit_rotation VALUES (1, 0)")
        index, = db.execute("SELECT next_index FROM outfit_rotation WHERE id = 1").fetchone()
        if not 0 <= index < len(OUTFITS):
            raise ValueError(f"Vị trí vòng xoay không hợp lệ trong {state_file}")
        db.execute(
            "UPDATE outfit_rotation SET next_index = ? WHERE id = 1",
            ((index + 1) % len(OUTFITS),),
        )
    return f"AVPM-{index + 1:02}", OUTFITS[index]


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text).casefold().replace("**", "").replace("__", "").replace("`", "")


def cli_product(value: str) -> str:
    key = re.sub(r"[\W_]+", "", normalize(value))
    for product in PRODUCTS:
        if key == normalize(product).replace(" ", ""):
            return product
    raise argparse.ArgumentTypeError(f"SKU hợp lệ gồm {', '.join(PRODUCTS)}")


def time_point(value: str) -> Decimal:
    parts = re.sub(UNIT, "", value).strip().replace(",", ".").split(":")
    return sum((Decimal(part) * (60 ** power) for power, part in enumerate(reversed(parts))), Decimal(0))


def scene_range(text: str) -> Decimal | None:
    match = TIME_RANGE.match(text)
    if match is None:
        return None
    start, end = match.group("start", "end")
    if not any(":" in point or re.search(UNIT, point) for point in (start, end)):
        return None
    return time_point(end) - time_point(start)


def scene_duration(text: str) -> Decimal | None:
    text = text.lstrip(" \t:-–—|([{")
    text = DURATION_FIELD.sub("", text).lstrip(" \t([{")
    duration = scene_range(text)
    if duration is not None:
        return duration
    match = TIME_SECONDS.match(text)
    return time_point(match["value"]) if match else None


def header_duration(text: str) -> Decimal | None:
    for field in re.split(r"[|\[(]", text):
        duration = scene_duration(field)
        if duration is not None:
            return duration
    return None


def continuous_prep(events: list[tuple[int, str]]) -> bool:
    steps: list[str] = []
    previous_scene = 0
    for scene, step in events:
        if scene > previous_scene + 1:
            steps.clear()
        previous_scene = scene
        if not steps or steps[-1] != step:
            steps.append(step)
        if tuple(steps[-4:]) in PREP_ORDERS:
            return True
    return False


def lint_script(text: str, product: str | None = None, *, poster: bool = False) -> list[Finding]:
    normalized = normalize(text)
    findings = []
    for pattern, level, label in (
        (EFFECTS, "ERROR", "Từ khóa hiệu ứng bị cấm"),
        (MEDICAL, "WARNING", "Cụm từ y tế bị cấm"),
    ):
        for match in pattern.finditer(normalized):
            line_number = normalized.count("\n", 0, match.start()) + 1
            phrase = " ".join(match[0].split())
            findings.append(Finding(level, line_number, f"{label} ‘{phrase}’."))
    if poster:
        return sorted(findings, key=lambda finding: finding.line or 0)

    scenes: list[Scene] = []
    prep_events = []
    for line_number, line in enumerate(normalized.splitlines(), start=1):
        header = SCENE_HEADER.match(line)
        range_seconds = scene_range(line.lstrip(" \t([{"))
        visual_text = VISUAL_EXCLUSIONS.split(line, maxsplit=1)[0]
        if header:
            scenes.append(Scene(line_number, header_duration(visual_text[header.end():])))
        elif range_seconds is not None:
            scenes.append(Scene(line_number, range_seconds))
        elif scenes and scenes[-1].seconds is None and DURATION_FIELD.match(line.strip()):
            scenes[-1].seconds = scene_duration(line)
        elif SCENE_DURATION_FIELD.match(line):
            scenes.append(Scene(line_number, scene_duration(line)))

        for match in PREP.finditer(visual_text):
            if not PREP_NEGATION.search(visual_text, 0, match.start()):
                prep_events.append((len(scenes), match.lastgroup))

    for scene in scenes:
        if scene.seconds is None:
            findings.append(Finding("WARNING", scene.line, "Cảnh thiếu thời lượng hoặc mốc cắt đọc được."))
        elif not MIN_SECONDS <= scene.seconds <= MAX_SECONDS:
            findings.append(Finding("ERROR", scene.line, f"Cảnh dài {scene.seconds:f}s, ngoài dải 1.8s–2.7s."))

    named_products = [name for name in PRODUCTS if re.search(
        r"\b" + r"[\s_-]*".join(map(re.escape, normalize(name).split())) + r"\b", normalized
    )]
    if scenes:
        prep_events = [(scene, step) for scene, step in prep_events if scene]
    if (product or named_products or STICK.search(normalized)) and not continuous_prep(prep_events):
        present_steps = {step for _, step in prep_events}
        missing_steps = [name for step, name in PREP_STEPS.items() if step not in present_steps]
        detail = f"thiếu {', '.join(missing_steps)}" if missing_steps else "sai thứ tự hoặc bị gián đoạn giữa các cảnh"
        sku = product or ", ".join(named_products) or "Gói bột"
        findings.append(Finding("ERROR", None, f"{sku} cần đủ 4 bước pha liền mạch, {detail}."))
    return sorted(findings, key=lambda finding: finding.line if finding.line is not None else len(normalized) + 1)


def self_test() -> None:
    from concurrent.futures import ThreadPoolExecutor

    with TemporaryDirectory() as directory:
        state = Path(directory) / "rotation.sqlite3"
        first_cycle = [next_outfit(state) for _ in OUTFITS]
        assert len(set(first_cycle)) == len(OUTFITS) == 16
        assert list(zip(*first_cycle))[1] == OUTFITS
        assert next_outfit(state) == first_cycle[0]
        assert next_outfit(state) == first_cycle[1]
        concurrent_state = Path(directory) / "concurrent.sqlite3"
        with ThreadPoolExecutor(max_workers=4) as pool:
            concurrent_cycle = list(pool.map(next_outfit, [concurrent_state] * 16))
        assert set(concurrent_cycle) == set(first_cycle)

    valid = (
        "**Cảnh 01 (2,4 giây):** Xé mép gói và đổ bột vào ly.\n"
        "Cảnh 02 [00:02.4–00:05.1]: Thêm nước, khuấy đều.\n"
    )
    assert lint_script("AV Protein\n" + valid) == []
    assert lint_script(valid, "Bojomi") == []
    assert lint_script("Curcumilk Phyto\n" + valid.replace("Thêm nước, khuấy đều.", "Khuấy đều.")) == [
        Finding("ERROR", None, "Curcumilk Phyto cần đủ 4 bước pha liền mạch, thiếu thêm nước.")
    ]
    assert lint_script("Collamela\n" + valid.replace("Cảnh 02", "Cảnh 02 (2s): Mở rèm.\nCảnh 03")) == [
        Finding("ERROR", None, "Collamela cần đủ 4 bước pha liền mạch, sai thứ tự hoặc bị gián đoạn giữa các cảnh.")
    ]
    assert lint_script("Cảnh 1 (2s): Thêm nước rồi xé gói.\nCảnh 2 (2s): Đổ bột, khuấy đều.", "Bojomi") == []
    assert lint_script("Lời thoại: Xé gói, đổ bột, thêm nước, khuấy đều.", "Bojomi")[0].level == "ERROR"
    assert lint_script("Cảnh 1 (2s): Không xé gói, đổ bột, thêm nước, khuấy đều.", "Bojomi")[0].level == "ERROR"
    assert lint_script("Xé gói, đổ bột.\nCảnh 1 (2s): Thêm nước, khuấy đều.", "Bojomi")[0].level == "ERROR"
    assert lint_script("Cảnh 1 (1.8s): Mở cửa.\nScene 2 [2.7s]: Mở rèm.") == []
    assert lint_script("Cảnh 1 (1.7s): Mở cửa.")[0].level == "ERROR"
    assert lint_script("[00:00–00:03.2] Mở rèm.")[0].level == "ERROR"
    assert lint_script("Cảnh 1 | Mở rèm | (0s đến 3.2s)")[0].level == "ERROR"
    assert lint_script("Thời lượng cảnh: 3.2s")[0].level == "ERROR"
    assert lint_script("Cảnh 1\nThời lượng: 2s\nHình: Mở rèm.") == []
    assert lint_script("Cảnh 1: Hình mở rèm.")[0].level == "WARNING"
    assert lint_script("Video dài 15s. Cốc nước dùng ở cuối video.") == []
    invalid = "Cảnh 01 (3.1s): Sparkle, glitter, bling-bling, kim tuyến, lấp lánh.\nThuốc đặc trị, chữa khỏi dứt điểm."
    findings = lint_script(invalid)
    assert sum(f.level == "ERROR" and "hiệu ứng" in f.message for f in findings) == 6
    assert sum(f.level == "ERROR" and "3.1s" in f.message for f in findings) == 1
    assert sum(f.level == "WARNING" and "y tế" in f.message for f in findings) == 2
    assert lint_script("Collamela — một gói bột cho buổi sáng.", poster=True) == []
    assert lint_script("Poster Collamela có glitter.", poster=True)[0].level == "ERROR"
    assert cli_product("AV_Protein") == "AV Protein"
    print("SELF_TEST_OK")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument("--next-outfit", action="store_true", help="Chọn và lưu bộ kế tiếp trong vòng 16 bộ.")
    command.add_argument("--lint-script", type=Path, metavar="FILE", help="Kiểm kịch bản hoặc prompt UTF-8.")
    command.add_argument("--self-test", action="store_true", help="Kiểm vòng xoay và lint bằng dữ liệu mẫu.")
    parser.add_argument("--product", type=cli_product, metavar="SKU", help=f"Chỉ định SKU khi lint video ({', '.join(PRODUCTS)}).")
    parser.add_argument("--poster", action="store_true", help="Kiểm từ khóa trong nội dung poster.")
    parser.add_argument("--state-file", type=Path, metavar="FILE", help="Đường dẫn SQLite dùng chung với --next-outfit.")
    args = parser.parse_args()
    if (args.product or args.poster) and not args.lint_script:
        parser.error("--product và --poster dùng cùng --lint-script.")
    if args.product and args.poster:
        parser.error("--product dành cho kịch bản video.")
    if args.state_file and not args.next_outfit:
        parser.error("--state-file dùng cùng --next-outfit.")

    if args.self_test:
        self_test()
        return 0
    try:
        if args.next_outfit:
            code, outfit = next_outfit(args.state_file or DEFAULT_STATE)
            print(f"{code}\t{outfit}")
            return 0
        text = args.lint_script.read_text(encoding="utf-8-sig")
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))
    if not text.strip():
        parser.error(f"Tệp trống: {args.lint_script}")

    findings = lint_script(text, args.product, poster=args.poster)
    for finding in findings:
        location = f" dòng {finding.line}" if finding.line is not None else ""
        print(f"{finding.level}{location}: {finding.message}")
    if any(finding.level == "ERROR" for finding in findings):
        print("LINT_FAILED")
        return 1
    print("LINT_WARNINGS" if findings else "LINT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
