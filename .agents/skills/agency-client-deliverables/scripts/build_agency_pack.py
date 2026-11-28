#!/usr/bin/env python3
"""Xuất kế hoạch nội dung, Media Plan và hồ sơ nghiệm thu Agency V6."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from hashlib import sha256
from html import escape
from importlib import import_module
from pathlib import Path
import json
import os
import re
from shutil import copy2
import sys
from tempfile import TemporaryDirectory
from textwrap import wrap
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


CONTENT_FILE = "Ke_Hoach_Noi_Dung.md"
MEDIA_FILE = "Media_Plan.xlsx"
REPORT_NAME = "Bao_Cao_Nghiem_Thu"
REPORT_FILES = tuple(REPORT_NAME + extension for extension in (".docx", ".html", ".md"))
RATIOS = ("16:9", "9:16")
HOOKS = ("pain", "desire", "contrarian")
VND_FORMAT = '#,##0" ₫"'
DATE_FORMAT = "dd/mm/yyyy"
BRAND_COLORS = {
    "htpm": "155E63", "hang thu pharma": "155E63",
    "avpm": "265838", "an vuong pharma": "265838",
    "viet han thien trang": "175382", "viet han": "175382", "thien trang": "175382",
    "salon spa": "6C4352", "salon": "6C4352", "spa": "6C4352",
    "bds": "785522", "bat dong san": "785522",
}
XML_FORBIDDEN = re.compile(r"[^\t\n\r\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]")


@dataclass(frozen=True)
class Script:
    id: str
    title: str
    hooks: tuple[str, ...]
    body: str
    cta: str


@dataclass(frozen=True)
class Media:
    date: date
    channel: str
    placement: str
    script_id: str
    ratio: str
    budget_vnd: int
    kpi: str
    status: str


@dataclass(frozen=True)
class Video:
    script_id: str
    ratio: str
    path: Path


@dataclass(frozen=True)
class Plan:
    brand: str
    campaign: str
    color: str
    audience: str
    objectives: list[str]
    scripts: list[Script]
    media: list[Media]
    videos: list[Video]


def required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} phải là chuỗi có nội dung.")
    if XML_FORBIDDEN.search(value):
        raise ValueError(f"{field} chứa ký tự không hợp lệ trong Excel hoặc Word.")
    return value.strip().replace("\r\n", "\n").replace("\r", "\n")


def required_object(value: object, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{field} phải là object JSON.")
    return value


def rows(data: dict, key: str, *, optional: bool = False):
    values = data.get(key, [] if optional else None)
    if not isinstance(values, list) or (not optional and not values):
        expected = "một mảng" if optional else "một mảng có ít nhất một dòng"
        raise ValueError(f"{key} phải là {expected}.")
    for number, value in enumerate(values, start=1):
        field = f"{key} dòng {number}"
        yield field, value


def brand_color(brand: str, override: object) -> str:
    if override is not None:
        color = required_text(override, "brand_color").removeprefix("#")
        if not re.fullmatch(r"[A-Fa-f0-9]{6}", color):
            raise ValueError("brand_color phải có dạng #RRGGBB.")
        return color.upper()
    folded = unicodedata.normalize("NFKD", brand.casefold().replace("đ", "d"))
    folded = "".join(char for char in folded if not unicodedata.combining(char))
    return BRAND_COLORS.get(" ".join(re.findall(r"[a-z0-9]+", folded)), "245169")


def script_reference(entry: dict, field: str, ids: set[str]) -> tuple[str, str]:
    script_id = required_text(entry.get("script_id"), f"{field}.script_id")
    ratio = required_text(entry.get("ratio"), f"{field}.ratio")
    if script_id not in ids:
        raise ValueError(f"{field}.script_id chưa có trong scripts ({script_id}).")
    if ratio not in RATIOS:
        raise ValueError(f"{field}.ratio phải là 16:9 hoặc 9:16.")
    return script_id, ratio


def load_plan(path: Path, brand: str, campaign: str) -> Plan:
    data = required_object(json.loads(path.read_text(encoding="utf-8-sig")), "Kế hoạch")
    brand = required_text(brand, "--brand")
    campaign = required_text(campaign, "--campaign")
    color = brand_color(brand, data.get("brand_color"))
    audience = required_text(data.get("audience"), "audience")
    objectives = [required_text(value, field) for field, value in rows(data, "objectives")]

    ids: set[str] = set()
    scripts = []
    for field, value in rows(data, "scripts"):
        entry = required_object(value, field)
        script_id = required_text(entry.get("id"), f"{field}.id")
        if script_id in ids:
            raise ValueError(f"Trùng mã kịch bản {script_id} ({field}).")
        ids.add(script_id)
        hooks = required_object(entry.get("hooks"), f"{field}.hooks")
        scripts.append(Script(
            script_id,
            required_text(entry.get("title"), f"{field}.title"),
            tuple(required_text(hooks.get(key), f"{field}.hooks.{key}") for key in HOOKS),
            required_text(entry.get("body"), f"{field}.body"),
            required_text(entry.get("cta"), f"{field}.cta"),
        ))

    media = []
    for field, value in rows(data, "media"):
        entry = required_object(value, field)
        script_id, ratio = script_reference(entry, field, ids)
        day = required_text(entry.get("date"), f"{field}.date")
        try:
            publish_date = date.fromisoformat(day)
            if publish_date.isoformat() != day or publish_date.year < 1900:
                raise ValueError(day)
        except ValueError as error:
            raise ValueError(f"{field}.date phải là ngày hợp lệ YYYY-MM-DD từ năm 1900.") from error
        budget = entry.get("budget_vnd")
        if type(budget) is not int or not 0 <= budget < 10**15:
            raise ValueError(f"{field}.budget_vnd phải là số nguyên VNĐ không âm, tối đa 15 chữ số.")
        media.append(Media(
            publish_date,
            required_text(entry.get("channel"), f"{field}.channel"),
            required_text(entry.get("placement"), f"{field}.placement"),
            script_id, ratio, budget,
            required_text(entry.get("kpi"), f"{field}.kpi"),
            required_text(entry.get("status", "Dự kiến"), f"{field}.status"),
        ))
    media.sort(key=lambda entry: entry.date)

    seen_paths: set[Path] = set()
    videos = []
    for field, value in rows(data, "videos", optional=True):
        entry = required_object(value, field)
        script_id, ratio = script_reference(entry, field, ids)
        video_path = path.parent.joinpath(required_text(entry.get("path"), f"{field}.path")).resolve()
        if video_path.suffix.casefold() != ".mp4":
            raise ValueError(f"{field}.path phải dẫn tới tệp MP4.")
        if video_path in seen_paths:
            raise ValueError(f"{field}.path trùng một Video Final đã khai ({video_path.name}).")
        seen_paths.add(video_path)
        videos.append(Video(script_id, ratio, video_path))
    return Plan(brand, campaign, color, audience, objectives, scripts, media, videos)


@dataclass(frozen=True)
class Formula:
    expression: str
    cached_value: int
    currency: bool = False


@dataclass(frozen=True)
class Sheet:
    name: str
    widths: tuple[int, ...]
    heading: tuple[str, ...]
    rows: list[tuple]
    filter_rows: bool = False


def workbook_sheets(plan: Plan) -> tuple[Sheet, Sheet]:
    budget = sum(entry.budget_vnd for entry in plan.media)
    if budget >= 10**15:
        raise ValueError("Tổng ngân sách vượt 15 chữ số mà Excel lưu chính xác.")
    ratios = [entry.ratio for entry in plan.media]
    summary = Sheet("Tổng quan", (30, 65), ("Chỉ tiêu", "Giá trị"), [
        ("Thương hiệu", plan.brand),
        ("Chiến dịch", plan.campaign),
        ("Tổng ngân sách", Formula("SUM('Media Plan'!F:F)", budget, currency=True)),
        *((f"Lượt phân phối {ratio}", Formula(
            f'COUNTIF(\'Media Plan\'!E:E,"{ratio}")', ratios.count(ratio))) for ratio in RATIOS),
    ])
    schedule = Sheet(
        "Media Plan", (15, 19, 26, 16, 12, 22, 32, 20),
        ("Ngày", "Kênh", "Vị trí", "Mã kịch bản", "Tỷ lệ", "Ngân sách VNĐ", "KPI", "Trạng thái"),
        [(item.date, item.channel, item.placement, item.script_id, item.ratio,
          item.budget_vnd, item.kpi, item.status) for item in plan.media], True,
    )
    for sheet in (summary, schedule):
        if len(sheet.rows) >= 1_048_576:
            raise ValueError(f"Trang {sheet.name} vượt giới hạn số dòng Excel.")
        for number, row in enumerate(sheet.rows, start=2):
            if any(isinstance(cell, str) and len(cell) > 32_767 for cell in row):
                raise ValueError(f"Trang {sheet.name}, dòng {number} có ô dài hơn 32.767 ký tự.")
    return summary, schedule


def header_ink(color: str) -> str:
    channels = [int(color[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    luminance = sum(weight * (channel / 12.92 if channel <= .04045 else ((channel + .055) / 1.055) ** 2.4)
                    for weight, channel in zip((.2126, .7152, .0722), channels))
    return "000000" if luminance > .179 else "FFFFFF"


def row_height(row: tuple, widths: tuple[int, ...]) -> int:
    lines = max((sum(max(1, len(wrap(line, max(1, width - 2)))) for line in cell.split("\n"))
                 for width, cell in zip(widths, row) if isinstance(cell, str)), default=1)
    return min(400, max(23, lines * 15 + 5))


def cell_style(row_number: int, value: object) -> int:
    if row_number == 1:
        return 1
    if isinstance(value, date):
        return 3
    if isinstance(value, int) or (isinstance(value, Formula) and value.currency):
        return 2
    return 4


def write_openpyxl(path: Path, sheets: tuple[Sheet, ...], color: str) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    workbook = Workbook()
    workbook.remove(workbook.active)
    heading_font = Font(name="Calibri", bold=True, color="FF" + header_ink(color))
    heading_fill = PatternFill("solid", fgColor="FF" + color)
    cell_alignment = Alignment(vertical="center", wrap_text=True)
    for sheet in sheets:
        page = workbook.create_sheet(sheet.name)
        page.freeze_panes = "A2"
        page.sheet_view.showGridLines = False
        page.sheet_properties.tabColor = "FF" + color
        for column, width in enumerate(sheet.widths, start=1):
            page.column_dimensions[get_column_letter(column)].width = width
        for number, row in enumerate((sheet.heading, *sheet.rows), start=1):
            page.row_dimensions[number].height = 29 if number == 1 else row_height(row, sheet.widths)
            for column, value in enumerate(row, start=1):
                cell = page.cell(number, column, "=" + value.expression if isinstance(value, Formula) else value)
                style = cell_style(number, value)
                cell.alignment = cell_alignment
                if isinstance(value, str):
                    cell.data_type = "s"
                if style == 1:
                    cell.fill = heading_fill
                    cell.font = heading_font
                elif style == 2:
                    cell.number_format = VND_FORMAT
                elif style == 3:
                    cell.number_format = DATE_FORMAT
        if sheet.filter_rows:
            page.auto_filter.ref = page.dimensions
    workbook.calculation.fullCalcOnLoad = True
    workbook.save(path)


SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def spreadsheet_styles(color: str) -> bytes:
    # Style indices are shared with cell_style(). Custom formats start at 164.
    alignment = '<alignment vertical="center" wrapText="1"/>'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<styleSheet xmlns="{SPREADSHEET_NS}">
  <numFmts count="2"><numFmt numFmtId="164" formatCode="{escape(VND_FORMAT)}"/>
    <numFmt numFmtId="165" formatCode="{DATE_FORMAT}"/></numFmts>
  <fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>
    <font><b/><color rgb="FF{header_ink(color)}"/><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="3"><fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF{color}"/><bgColor indexed="64"/></patternFill></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="5">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1">{alignment}</xf>
    <xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1">{alignment}</xf>
    <xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1">{alignment}</xf>
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1">{alignment}</xf>
  </cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''.encode("utf-8")


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def worksheet_xml(sheet: Sheet, color: str) -> bytes:
    page = ET.Element("worksheet", {"xmlns": SPREADSHEET_NS})
    properties = ET.SubElement(page, "sheetPr")
    ET.SubElement(properties, "tabColor", rgb="FF" + color)
    ref = f"A1:{chr(64 + len(sheet.widths))}{len(sheet.rows) + 1}"
    ET.SubElement(page, "dimension", ref=ref)
    views = ET.SubElement(page, "sheetViews")
    view = ET.SubElement(views, "sheetView", workbookViewId="0", showGridLines="0")
    ET.SubElement(view, "pane", ySplit="1", topLeftCell="A2", activePane="bottomLeft", state="frozen")
    ET.SubElement(view, "selection", pane="bottomLeft", activeCell="A2", sqref="A2")
    ET.SubElement(page, "sheetFormatPr", defaultRowHeight="23")
    columns = ET.SubElement(page, "cols")
    for index, width in enumerate(sheet.widths, start=1):
        ET.SubElement(columns, "col", min=str(index), max=str(index), width=str(width), customWidth="1")
    data = ET.SubElement(page, "sheetData")
    for number, values in enumerate((sheet.heading, *sheet.rows), start=1):
        height = 29 if number == 1 else row_height(values, sheet.widths)
        row = ET.SubElement(data, "row", r=str(number), ht=str(height), customHeight="1")
        for column, value in enumerate(values, start=1):
            cell = ET.SubElement(row, "c", r=f"{chr(64 + column)}{number}", s=str(cell_style(number, value)))
            if isinstance(value, str):
                cell.set("t", "inlineStr")
                inline = ET.SubElement(cell, "is")
                ET.SubElement(inline, "t", {"xml:space": "preserve"}).text = value
                continue
            if isinstance(value, Formula):
                ET.SubElement(cell, "f").text = value.expression
                value = value.cached_value
            elif isinstance(value, date):
                # Match Excel's 1900 epoch, including its reserved serial 60.
                value = (value - date(1899, 12, 31)).days + (value >= date(1900, 3, 1))
            ET.SubElement(cell, "v").text = str(value)
    if sheet.filter_rows:
        ET.SubElement(page, "autoFilter", ref=ref)
    return xml_bytes(page)


def write_spreadsheetml(path: Path, sheets: tuple[Sheet, ...], color: str) -> None:
    types = ET.Element("Types", xmlns=CONTENT_NS)
    ET.SubElement(types, "Default", Extension="rels", ContentType="application/vnd.openxmlformats-package.relationships+xml")
    ET.SubElement(types, "Default", Extension="xml", ContentType="application/xml")
    for part, kind in [("workbook", "sheet.main"), ("styles", "styles"),
                       *((f"worksheets/sheet{i}", "worksheet") for i in range(1, len(sheets) + 1))]:
        ET.SubElement(types, "Override", PartName=f"/xl/{part}.xml", ContentType=f"application/vnd.openxmlformats-officedocument.spreadsheetml.{kind}+xml")
    package = ET.Element("Relationships", xmlns=PACKAGE_REL_NS)
    ET.SubElement(package, "Relationship", Id="rId1", Type=f"{OFFICE_REL_NS}/officeDocument", Target="xl/workbook.xml")
    book = ET.Element("workbook", {"xmlns": SPREADSHEET_NS, "xmlns:r": OFFICE_REL_NS})
    ET.SubElement(ET.SubElement(book, "bookViews"), "workbookView", activeTab="0")
    tabs = ET.SubElement(book, "sheets")
    relationships = ET.Element("Relationships", xmlns=PACKAGE_REL_NS)
    ET.SubElement(relationships, "Relationship", Id="rIdStyles", Type=f"{OFFICE_REL_NS}/styles", Target="styles.xml")
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for index, sheet in enumerate(sheets, start=1):
            rel_id = f"rId{index}"
            target = f"worksheets/sheet{index}.xml"
            ET.SubElement(tabs, "sheet", {"name": sheet.name, "sheetId": str(index), "r:id": rel_id})
            ET.SubElement(relationships, "Relationship", Id=rel_id, Type=f"{OFFICE_REL_NS}/worksheet", Target=target)
            archive.writestr(f"xl/{target}", worksheet_xml(sheet, color))
        ET.SubElement(book, "calcPr", calcId="191029", calcMode="auto", fullCalcOnLoad="1")
        archive.writestr("[Content_Types].xml", xml_bytes(types))
        archive.writestr("_rels/.rels", xml_bytes(package))
        archive.writestr("xl/workbook.xml", xml_bytes(book))
        archive.writestr("xl/_rels/workbook.xml.rels", xml_bytes(relationships))
        archive.writestr("xl/styles.xml", spreadsheet_styles(color))


@dataclass(frozen=True)
class QCResult:
    status: str
    detail: str


def gate_fingerprint(path: Path) -> tuple[int, str]:
    # Match edit/canvas-tools/video_qc_gate.py, including the small-file rule.
    with path.open("rb") as source:
        stat = os.fstat(source.fileno())
        digest = sha256(source.read(65_536))
        if stat.st_size > 131_072:
            source.seek(stat.st_size - 65_536)
            digest.update(source.read(65_536))
        after = path.stat()
        if (after.st_size, after.st_mtime_ns) != (stat.st_size, stat.st_mtime_ns):
            raise OSError("Video đã thay đổi trong lúc đối chiếu.")
    return stat.st_size, digest.hexdigest()


def check_qc(path: Path) -> QCResult:
    if not path.is_file():
        return QCResult("Chờ QC", "Chưa tìm thấy tệp MP4.")
    certificate_path = path.with_name(path.name + ".qc_pass.json")
    try:
        cert = required_object(json.loads(certificate_path.read_text(encoding="utf-8-sig")), "Chứng nhận QC")
        verdict = cert.get("verdict")
        if verdict not in ("PASS", "FAIL") or cert.get("auditor_verified") is not (verdict == "PASS"):
            raise ValueError("Trạng thái QC không hợp lệ.")
        auditor = required_text(cert.get("auditor"), "Kiểm duyệt viên")
        signed = datetime.fromisoformat(required_text(cert.get("signed_at"), "Thời điểm kiểm duyệt"))
        if verdict == "PASS" and len(required_text(cert.get("notes"), "Ghi chú QC")) < 30:
            raise ValueError("Ghi chú QC chưa hợp lệ.")
        if type(cert.get("file_size")) is not int or not re.fullmatch(r"[a-f0-9]{64}", str(cert.get("sha256_head_tail"))):
            raise ValueError("Fingerprint chưa hợp lệ.")
    except FileNotFoundError:
        return QCResult("Chờ QC", "Chưa có chứng nhận cạnh MP4.")
    except (OSError, ValueError, RecursionError):
        return QCResult("Chờ QC", "Không đọc được chứng nhận hợp lệ.")
    try:
        size, digest = gate_fingerprint(path)
    except OSError:
        return QCResult("Chờ QC", "Không đọc được MP4 để đối chiếu fingerprint.")
    if (size, digest) != (cert["file_size"], cert["sha256_head_tail"]):
        return QCResult("Chờ QC", "Fingerprint không khớp với MP4 hiện tại.")
    return QCResult(verdict, f"{auditor} · {signed:%d/%m/%Y %H:%M}")


@dataclass(frozen=True)
class Table:
    headers: tuple[str, ...]
    rows: list[tuple[str, ...]]
    widths: tuple[float, ...]


@dataclass(frozen=True)
class Section:
    title: str
    blocks: tuple[str | list[str] | Table, ...]


def hook_matrix(plan: Plan) -> Table:
    return Table(
        ("Mã · Chủ đề", "Pain · Nỗi đau", "Desire · Khao khát", "Contrarian · Góc nhìn ngược"),
        [(f"{script.id} · {script.title}", *script.hooks) for script in plan.scripts],
        (3.6, 4.45, 4.45, 4.5),
    )


def report_sections(plan: Plan) -> tuple[str, tuple[Section, ...]]:
    expected = list(dict.fromkeys((item.script_id, item.ratio) for item in plan.media))
    represented = {(video.script_id, video.ratio) for video in plan.videos}
    missing = [pair for pair in expected if pair not in represented]
    inventory = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)
    for video in plan.videos:
        qc = check_qc(video.path)
        counts[qc.status] += 1
        inventory[video.ratio].append((video.script_id, video.path.name, f"{qc.status}\n{qc.detail}"))
    for script_id, ratio in missing:
        inventory[ratio].append((script_id, "Chưa có bản Final trong hồ sơ.", "Chờ QC"))

    status = "FAIL" if counts["FAIL"] else "Chờ QC"
    if plan.videos and not missing and counts["PASS"] == len(plan.videos):
        status = "PASS"
    title = "Báo cáo nghiệm thu chiến dịch" if status == "PASS" else "Đề án bàn giao chiến dịch"
    totals = (
        f"{counts['PASS']} PASS · {counts['FAIL']} FAIL · {counts['Chờ QC']} tệp chờ QC"
        f" · {len(missing)} bản theo lịch còn thiếu"
    )
    sections = [
        Section("Mục tiêu chiến dịch", (plan.objectives,)),
        Section("Ma trận kịch bản 3-Hook", (hook_matrix(plan),)),
    ]
    for ratio in RATIOS:
        video_table = Table(("Mã kịch bản", "Tệp bàn giao", "Kết quả QC"), inventory[ratio], (2.8, 7.7, 6.5))
        content = video_table if video_table.rows else "Chưa có video thuộc tỷ lệ này trong phạm vi bàn giao."
        sections.append(Section(f"Danh mục Video Final {ratio}", (content,)))
    sections.append(Section("Chứng nhận nghiệm thu", (f"video-qc-gate {status}", totals)))
    return title, tuple(sections)


def markdown_text(value: str) -> str:
    return re.sub(r"([\\`*_\[\]|#!~])", r"\\\1", escape(value, quote=False)).replace("\n", "<br>")


def markdown_sections(sections: tuple[Section, ...]) -> str:
    chunks = []
    for section in sections:
        chunks.append(f"## {markdown_text(section.title)}")
        for block in section.blocks:
            if isinstance(block, Table):
                lines = ["| " + " | ".join(map(markdown_text, block.headers)) + " |"]
                lines.append("| " + " | ".join("---" for _ in block.headers) + " |")
                lines.extend("| " + " | ".join(map(markdown_text, row)) + " |" for row in block.rows)
                chunks.append("\n".join(lines))
            elif isinstance(block, list):
                chunks.append("\n".join(f"- {markdown_text(item)}" for item in block))
            else:
                chunks.append(markdown_text(block))
    return "\n\n".join(chunks)


def write_markdown(path: Path, title: str, identity: str, sections: tuple[Section, ...]) -> None:
    text = f"# {markdown_text(title)}\n\n{markdown_text(identity)}\n\n{markdown_sections(sections)}\n"
    path.write_text(text, encoding="utf-8")


def write_content_plan(path: Path, plan: Plan, identity: str) -> None:
    sections = (
        Section("Mục tiêu chiến dịch", (plan.objectives,)),
        Section("Đối tượng", (plan.audience,)),
        Section("Ma trận kịch bản 3-Hook", (hook_matrix(plan),)),
        *(Section(f"{script.id} · {script.title}", (script.body, f"CTA · {script.cta}")) for script in plan.scripts),
    )
    write_markdown(path, "Kế hoạch nội dung", identity, sections)


def write_html(path: Path, title: str, identity: str, color: str, sections: tuple[Section, ...]) -> None:
    def html_text(value: str) -> str:
        return escape(value).replace("\n", "<br>")

    markup = []
    for section in sections:
        markup.append(f"<section><h2>{html_text(section.title)}</h2>")
        for block in section.blocks:
            if isinstance(block, Table):
                columns = "".join(f'<col style="width:{100 * width / sum(block.widths):.2f}%">' for width in block.widths)
                headers = "".join(f'<th scope="col">{html_text(value)}</th>' for value in block.headers)
                body = "".join("<tr>" + "".join(f"<td>{html_text(value)}</td>" for value in row) + "</tr>" for row in block.rows)
                markup.append(f"<table><colgroup>{columns}</colgroup><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>")
            elif isinstance(block, list):
                markup.append("<ul>" + "".join(f"<li>{html_text(value)}</li>" for value in block) + "</ul>")
            else:
                markup.append(f"<p>{html_text(block)}</p>")
        markup.append("</section>")
    path.write_text(f'''<!doctype html>
<html lang="vi">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
@page {{ size: A4; margin: 19mm 20mm; }}
:root {{ color-scheme: light; print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #edf1f4; color: #172634; font: 11pt/1.48 Calibri, Arial, sans-serif; }}
main {{ max-width: 210mm; margin: 28px auto; padding: 19mm 20mm; background: white; box-shadow: 0 10px 36px #13213220; }}
header {{ border-left: 4px solid #{color}; padding-left: 12pt; margin-bottom: 21pt; }}
h1 {{ margin: 0 0 4pt; color: #000; font: bold 26pt/1.12 Georgia, serif; }}
h2 {{ margin: 17pt 0 6pt; color: #000; font-size: 13pt; break-after: avoid; }}
h1, h2, p, td, th, li {{ overflow-wrap: anywhere; }}
p, ul {{ margin: 0 0 5pt; }}
ul {{ padding-left: 15pt; }}
table {{ width: 100%; border-collapse: collapse; table-layout: fixed; font-size: 9.5pt; }}
th, td {{ padding: 5pt 6pt; border: 1px solid #d9d9d9; text-align: left; vertical-align: middle; }}
th {{ color: white; background: #203a54; }}
tbody tr:nth-child(even) {{ background: #f4f7fa; }}
section:last-child p:first-of-type {{ font-weight: bold; }}
@media print {{
  body {{ background: white; }}
  main {{ margin: 0; padding: 0; max-width: none; box-shadow: none; }}
  thead {{ display: table-header-group; }}
  tr, header {{ break-inside: avoid; }}
}}
</style></head>
<body><main>
<header><h1>{html_text(title)}</h1><p>{html_text(identity)}</p></header>
{chr(10).join(markup)}
</main></body></html>
''', encoding="utf-8")


def write_docx(path: Path, title: str, identity: str, sections: tuple[Section, ...]) -> None:
    from docx import Document
    from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor

    def word_element(tag: str, **attrs) -> OxmlElement:
        element = OxmlElement(f"w:{tag}")
        for name, value in attrs.items():
            element.set(qn(f"w:{name}"), str(value))
        return element

    document = Document()
    document.core_properties.title = title
    document.core_properties.author = "Full Studio"
    page = document.sections[0]
    page.page_height, page.page_width = Cm(29.7), Cm(21)
    page.left_margin = page.right_margin = Cm(2)
    page.top_margin = page.bottom_margin = Cm(1.9)
    for key, family, size, before, after in (
        ("Normal", "Calibri", 11, 0, 5),
        ("Title", "Georgia", 26, 0, 5),
        ("Subtitle", "Calibri", 11, 0, 12),
        ("Heading 1", "Calibri", 13, 13, 5),
    ):
        style = document.styles[key]
        style.font.name, style.font.size = family, Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.13
        for border in style.element.xpath("./w:pPr/w:pBdr"):
            border.getparent().remove(border)
    document.styles["Title"].font.bold = True
    document.add_paragraph(title, "Title")
    document.add_paragraph(identity, "Subtitle")

    for section in sections:
        document.add_heading(section.title, level=1)
        for block in section.blocks:
            if isinstance(block, str):
                paragraph = document.add_paragraph(block)
                if block.startswith("video-qc-gate "):
                    paragraph.runs[0].bold = True
                continue
            if isinstance(block, list):
                for item in block:
                    document.add_paragraph(item, "List Bullet")
                continue

            table = document.add_table(rows=1, cols=len(block.headers))
            table.autofit = False
            table_properties = table._tbl.tblPr
            borders = word_element("tblBorders")
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                borders.append(word_element(edge, val="single", sz=4, color="D9D9D9"))
            table_properties.insert_element_before(borders, "w:tblLayout")
            margins = word_element("tblCellMar")
            for edge in ("top", "left", "bottom", "right"):
                margins.append(word_element(edge, w=90 if edge in ("top", "bottom") else 105, type="dxa"))
            table_properties.append(margins)
            for column, width in zip(table.columns, block.widths):
                column.width = Cm(width)
            for index, values in enumerate((block.headers, *block.rows)):
                row = table.rows[0] if index == 0 else table.add_row()
                if index == 0:
                    row._tr.get_or_add_trPr().append(word_element("tblHeader", val="true"))
                for cell, value, width in zip(row.cells, values, block.widths):
                    cell.width = Cm(width)
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    paragraph = cell.paragraphs[0]
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.keep_with_next = index == 0
                    run = paragraph.add_run(value)
                    run.font.size = Pt(9.5)
                    fill = "203A54" if index == 0 else "FFFFFF" if index % 2 else "F4F7FA"
                    cell._tc.get_or_add_tcPr().append(word_element("shd", val="clear", fill=fill))
                    if index == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    document.save(path)


def module_available(name: str) -> bool:
    try:
        import_module(name)
    except ImportError:
        return False
    return True


def publish_pack(staged: Path, out_dir: Path, names: list[str]) -> list[Path]:
    """Publish staged files and restore any previous pack on a replace error."""
    lock = out_dir / ".agency-pack.lock"
    temporary_flag = getattr(os, "O_TEMPORARY", 0)
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL | temporary_flag)
    except FileExistsError as error:
        raise ValueError(f"Một lượt xuất đang dùng thư mục {out_dir}.") from error
    try:
        backups = staged / "previous"
        backups.mkdir()
        obsolete = [out_dir / name for name in REPORT_FILES if name not in names and (out_dir / name).exists()]
        destinations = [out_dir / name for name in names]
        for target in destinations + obsolete:
            if target.exists():
                copy2(target, backups / target.name)
        changed = []
        try:
            for target in destinations:
                (staged / target.name).replace(target)
                changed.append(target)
            for target in obsolete:
                target.unlink()
                changed.append(target)
        except (OSError, KeyboardInterrupt):
            for target in reversed(changed):
                backup = backups / target.name
                if backup.exists():
                    backup.replace(target)
                else:
                    target.unlink()
            raise
        return destinations
    finally:
        os.close(fd)
        if not temporary_flag:
            lock.unlink()


def build_pack(plan: Plan, out_dir: Path, *, force_fallback: bool = False) -> list[Path]:
    sheets = workbook_sheets(plan)
    title, sections = report_sections(plan)
    identity = f"{plan.brand} · {plan.campaign}"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = [CONTENT_FILE, MEDIA_FILE]
    with TemporaryDirectory(prefix=".agency-pack-", dir=out_dir) as directory:
        stage = Path(directory)
        write_content_plan(stage / CONTENT_FILE, plan, identity)
        if not force_fallback and module_available("openpyxl"):
            write_openpyxl(stage / MEDIA_FILE, sheets, plan.color)
        else:
            write_spreadsheetml(stage / MEDIA_FILE, sheets, plan.color)
        if not force_fallback and module_available("docx"):
            names.append(REPORT_NAME + ".docx")
            write_docx(stage / names[-1], title, identity, sections)
        else:
            names.extend((REPORT_NAME + ".html", REPORT_NAME + ".md"))
            write_html(stage / names[-2], title, identity, plan.color, sections)
            write_markdown(stage / names[-1], title, identity, sections)
        return publish_pack(stage, out_dir, names)


def self_test() -> None:
    sample = {
        "brand_color": "#19536A",
        "audience": "Khách hàng quan tâm đến dịch vụ",
        "objectives": ["Đạt 30 lượt đăng ký tư vấn trong hai tuần."],
        "scripts": [{"id": "V01", "title": "Các bước đăng ký",
                     "hooks": {"pain": "Chưa biết hỏi gì?", "desire": "Chuẩn bị trong 2 phút.",
                               "contrarian": "Bắt đầu bằng mục tiêu <dự kiến> | Bước 1."},
                     "body": "Chốt mục tiêu, chọn câu hỏi và đặt lịch.", "cta": "Đăng ký lịch tư vấn."}],
        "media": [{"date": "2026-12-05", "script_id": "V01", "ratio": "9:16", "channel": "Facebook",
                   "placement": "Reels", "budget_vnd": 1_250_000, "kpi": '=HYPERLINK("test")'},
                  {"date": "2026-12-04", "script_id": "V01", "ratio": "16:9", "channel": "YouTube",
                   "placement": "Video", "budget_vnd": 750_000, "kpi": "10 lượt đăng ký"}],
        "videos": [{"script_id": "V01", "ratio": ratio, "path": f"Final/{ratio.replace(':', 'x')}.mp4"}
                   for ratio in RATIOS],
    }

    def expect(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(message)

    with TemporaryDirectory(prefix="agency-v6-self-test-") as directory:
        root = Path(directory)
        plan_json = root / "kế hoạch.json"
        plan_json.write_text(json.dumps(sample, ensure_ascii=False), encoding="utf-8-sig")
        plan = load_plan(plan_json, "Việt Hàn - Thiện Trang", "Tư vấn & đặt lịch")
        expect(plan.color == "19536A" and brand_color("BĐS", None) == "785522", "Màu thương hiệu.")
        plan.videos[0].path.parent.mkdir()
        expect(check_qc(plan.videos[0].path).status == "Chờ QC", "MP4 còn thiếu.")

        for video, payload in zip(plan.videos, (b"a" * 90_000, b"b" * 70_000 + b"c" * 70_000)):
            video.path.write_bytes(payload)
            expect(check_qc(video.path).status == "Chờ QC", "Chứng nhận còn thiếu.")
            fingerprint = payload[:65_536] + (payload[-65_536:] if len(payload) > 131_072 else b"")
            cert = {"verdict": "PASS", "auditor_verified": True, "auditor": "Kiểm duyệt mẫu",
                    "signed_at": "2026-12-06T12:00:00", "notes": "Dữ liệu kiểm tra chỉ tồn tại trong self-test.",
                    "file_size": len(payload), "sha256_head_tail": sha256(fingerprint).hexdigest()}
            sidecar = video.path.with_name(video.path.name + ".qc_pass.json")
            sidecar.write_text(json.dumps(cert, ensure_ascii=False), encoding="utf-8")

        native_dir = root / "chuẩn"
        fallback_dir = root / "dự phòng"
        native = build_pack(plan, native_dir)
        fallback = build_pack(plan, fallback_dir, force_fallback=True)
        expect(fallback == build_pack(plan, fallback_dir, force_fallback=True), "Xuất lại cùng thư mục.")
        content = (fallback_dir / CONTENT_FILE).read_text(encoding="utf-8")
        expect(r"\| Bước 1" in content and "CTA · Đăng ký lịch tư vấn." in content, "Kế hoạch nội dung.")
        html_report = (fallback_dir / (REPORT_NAME + ".html")).read_text(encoding="utf-8")
        md_report = (fallback_dir / (REPORT_NAME + ".md")).read_text(encoding="utf-8")
        expect(all(value in html_report for value in ("size: A4", "&lt;dự kiến&gt;", "16x9.mp4", "9x16.mp4",
                                                     "Tư vấn &amp; đặt lịch", "video-qc-gate PASS")), "Báo cáo HTML.")
        expect("Ma trận kịch bản 3-Hook" in md_report and "video-qc-gate PASS" in md_report, "Báo cáo Markdown.")

        ns = {"m": SPREADSHEET_NS}
        for folder in (native_dir, fallback_dir):
            workbook_path = folder / MEDIA_FILE
            with ZipFile(workbook_path) as archive:
                expect(archive.testzip() is None, "Gói XLSX lỗi CRC.")
                for member in archive.namelist():
                    if member.endswith((".xml", ".rels")):
                        ET.fromstring(archive.read(member))
                summary = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
                schedule = ET.fromstring(archive.read("xl/worksheets/sheet2.xml"))
                formulas = [element.text for element in summary.findall(".//m:f", ns)]
                expect(formulas == ["SUM('Media Plan'!F:F)", 'COUNTIF(\'Media Plan\'!E:E,"16:9")',
                                    'COUNTIF(\'Media Plan\'!E:E,"9:16")'], "Công thức Excel.")
                expect(schedule.find(".//m:pane", ns).get("topLeftCell") == "A2", "Dòng tiêu đề cố định.")
                expect(schedule.find(".//m:c[@r='G3']", ns).get("t") == "inlineStr", "Ô nhập phải là văn bản.")
            if module_available("openpyxl"):
                from openpyxl import load_workbook

                workbook = load_workbook(workbook_path)
                try:
                    overview, calendar = workbook.worksheets
                    expect(overview["B4"].number_format == VND_FORMAT and calendar["F3"].number_format == VND_FORMAT,
                           "Định dạng VNĐ.")
                    expect(calendar["F3"].value == 1_250_000 and calendar["A2"].value.date() == date(2026, 12, 4),
                           "Ngân sách và ngày có kiểu dữ liệu số/ngày.")
                    expect(calendar["A1"].fill.fgColor.rgb == "FF19536A", "Màu tiêu đề bảng tính.")
                finally:
                    workbook.close()
        if module_available("openpyxl"):
            cached = load_workbook(fallback_dir / MEDIA_FILE, data_only=True)
            try:
                expect([cached.active[f"B{row}"].value for row in (4, 5, 6)] == [2_000_000, 1, 1], "Giá trị công thức dự phòng.")
            finally:
                cached.close()
        if module_available("docx"):
            from docx import Document

            report = Document(native_dir / (REPORT_NAME + ".docx"))
            expect(len(report.tables) == 3 and report.tables[1].cell(1, 1).text == "16x9.mp4", "Danh mục Word.")
            expect(round(report.sections[0].page_width.cm, 1) == 21 and round(report.sections[0].page_height.cm, 1) == 29.7,
                   "Khổ A4 trong Word.")
            expect(any(paragraph.text == "video-qc-gate PASS" for paragraph in report.paragraphs), "Chứng nhận Word.")
        expect(all(path.is_file() for path in native + fallback), "Gói bàn giao đủ tệp.")

        # A same-size change in the tail must invalidate the existing certificate.
        with plan.videos[-1].path.open("r+b") as video_file:
            video_file.seek(-1, os.SEEK_END)
            video_file.write(b"z")
        expect("Fingerprint không khớp" in check_qc(plan.videos[-1].path).detail, "Chứng nhận hết hiệu lực.")
        pending = build_pack(plan, native_dir, force_fallback=True)
        pending_report = pending[-1].read_text(encoding="utf-8")
        expect("Đề án bàn giao" in pending_report and "video-qc-gate PASS" not in pending_report, "Hồ sơ chờ QC.")
        expect(not (native_dir / (REPORT_NAME + ".docx")).exists(), "Dọn báo cáo thuộc định dạng xuất trước đó.")
        if module_available("docx"):
            build_pack(plan, native_dir)
            expect(not pending[-1].exists() and not pending[-2].exists(), "Dọn HTML và Markdown sau khi xuất Word.")

        sample["videos"].pop()
        plan_json.write_text(json.dumps(sample), encoding="utf-8")
        partial = load_plan(plan_json, "HTPM", "Thử nghiệm")
        title, sections = report_sections(partial)
        expect("Đề án" in title and "Chưa có bản Final" in markdown_sections(sections), "Thiếu tỷ lệ đã lên lịch.")
    print("SELF_TEST_OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand", help="Tên thương hiệu, ví dụ HTPM, AVPM, Việt Hàn - Thiện Trang, Salon/Spa hoặc BĐS.")
    parser.add_argument("--campaign", help="Tên chiến dịch.")
    parser.add_argument("--plan-json", type=Path, help="Đường dẫn kế hoạch JSON UTF-8.")
    parser.add_argument("--out-dir", type=Path, help="Thư mục nhận bộ hồ sơ.")
    parser.add_argument("--self-test", action="store_true", help="Kiểm tra gói mẫu trong thư mục tạm.")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    required = {"--brand": args.brand, "--campaign": args.campaign, "--plan-json": args.plan_json, "--out-dir": args.out_dir}
    missing = [flag for flag, value in required.items() if value is None]
    if missing:
        parser.error("thiếu " + ", ".join(missing))
    try:
        plan = load_plan(args.plan_json, args.brand, args.campaign)
        outputs = build_pack(plan, args.out_dir.resolve())
    except (OSError, ValueError, RecursionError, RuntimeError) as error:
        print(f"Lỗi xuất hồ sơ. {error}", file=sys.stderr)
        return 1
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
