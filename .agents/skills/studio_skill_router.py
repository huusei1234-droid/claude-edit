"""Tra cứu kho Full Studio V6 và gợi ý lệnh PowerShell cho từng kỹ năng."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import py_compile
import re
import sys
import tempfile
import unicodedata


SKILL_STORE = Path(".agents") / "skills"
AFTER_EFFECTS_KEYWORDS = ("after effects", "after effects 2027", "afterfx", "ae 2027", "ae2027", "lossless alpha")


@dataclass(frozen=True)
class Skill:
    guide: Path
    name: str
    description: str
    scripts: tuple[str, ...]
    templates: tuple[str, ...]

    @property
    def slug(self) -> str:
        return self.guide.parent.name


@dataclass(frozen=True)
class Route:
    priority: int
    skills: tuple[str, ...]
    keywords: tuple[str, ...]


# Kỹ năng đầu xử lý yêu cầu chính. Các mục sau hỗ trợ cùng quy trình.
ROUTES = (
    Route(150, ("phim-ai-flow-prompt", "video-qc-auditor", "hyperframes"),
          ("k4", "chuyện trong nhà", "drama gia đình", "phim cổ trang", "prompt flow",
           "flow prompt", "google flow", "phim ai", "ai short film", "flow storyboard")),
    Route(147, ("an-vuong-daily-autopilot", "agency-client-deliverables", "video-qc-auditor"),
          ("an vượng", "anvuong", "avpm", "chị hậu")),
    Route(145, ("talking-head-ngoi-ban", "talking-head-v3", "hyperframes"),
          ("ngồi bàn", "behind shoulder", "seated talking head", "desk talking head")),
    Route(102, ("talking-head-ngoi-ban", "talking-head-v3", "agency-client-deliverables"),
          ("htpm", "hằng thu pharma", "chị hằng")),
    Route(146, ("kobe-motion-talking-head", "hyperframes", "media-use"),
          ("kobe motion", "kobe", "circle pip", "dark cyber", "light pastel saas")),
    Route(136, ("talking-head-v3", "hyperframes", "video-qc-auditor"),
          ("talking head v3", "bojomi", "lt plus", "split b-roll")),
    Route(90, ("talking-head-v3", "talking-head-ngoi-ban", "hyperframes"),
          ("talking head", "chuyên gia tư vấn", "dược sĩ tư vấn")),
    Route(146, ("viet-han-video-ban-hang", "video-qc-auditor", "agency-client-deliverables"),
          ("việt hàn", "thiện trang", "bento y tế", "medical ads", "quảng cáo phòng khám")),
    Route(148, ("tvc-qc-san-pham", "hyperframes", "video-qc-auditor"),
          ("tvc sản phẩm", "tvc qc sản phẩm", "quảng cáo sản phẩm", "product tvc", "product commercial",
           "silk satin", "beat grid", "packshot")),
    Route(144, ("tvc-khong-gian-dich-vu", "tvc-qc-san-pham", "hyperframes"),
          ("salon", "spa", "showroom", "tvc dịch vụ", "tvc không gian", "tvc cơ sở",
           "tvc phòng khám", "tvc nhà hàng", "service tvc", "venue commercial", "lut nvenc")),
    Route(132, ("tvc-qc-san-pham", "tvc-khong-gian-dich-vu", "hyperframes"),
          AFTER_EFFECTS_KEYWORDS),
    Route(145, ("photoshop-pro-studio", "ps", "tvc-qc-san-pham"),
          ("psd", "BiRefNet", "retouch", "retouch ảnh", "cutout ảnh", "icc srgb", "poster 4 nhóm")),
    Route(149, ("ps", "photoshop-pro-studio"),
          ("generative fill", "generative expand", "firefly", "photoshop mcp")),
    Route(122, ("ps", "photoshop-pro-studio", "tvc-qc-san-pham"),
          ("photoshop", "ps", "ps 2026", "photoshop 2026")),
    Route(142, ("capcut-pro-editor", "video-qc-auditor", "media-use"),
          ("capcut", "draft_content.json", "micro fade", "micro zoom")),
    Route(142, ("premiere-pro-master-editor", "video-qc-auditor", "media-use"),
          ("premiere pro", "premiere", "xmeml", "final cut pro 7 xml", "fcp 7 xml")),
    Route(140, ("podcast-doanh-nhan-bds", "media-use", "video-qc-auditor"),
          ("podcast", "bđs", "bất động sản", "doanh nhân", "real estate", "business interview")),
    Route(160, ("agency-client-deliverables", "openai-xlsx", "openai-docx"),
          ("media plan", "agency pack", "bàn giao chiến dịch", "campaign handoff", "kế hoạch chiến dịch",
           "báo cáo nghiệm thu", "media planning")),
    Route(126, ("openai-xlsx", "agency-client-deliverables", "openai-docx"),
          ("xlsx", "xls", "csv", "tsv", "spreadsheet", "google sheets", "bảng tính", "excel")),
    Route(146, ("openai-excel-live", "openai-xlsx", "agency-client-deliverables"),
          ("excel live", "excel đang mở", "excel đang hoạt động", "open excel workbook", "excel add-in")),
    Route(125, ("openai-docx", "openai-pdf", "openai-template-creator"),
          ("docx", "microsoft word", "word", "google docs", "redline")),
    Route(130, ("openai-pdf", "openai-docx", "openai-template-creator"),
          ("pdf", "acroform", "poppler")),
    Route(130, ("openai-pptx", "slideshow", "openai-template-creator"),
          ("pptx", "powerpoint", "google slides", "presentation", "slide deck", "bài thuyết trình")),
    Route(150, ("openai-template-creator", "openai-docx", "openai-pptx"),
          ("template skill", "tạo skill mẫu", "reusable template", "mẫu tái sử dụng")),
    Route(152, ("reverse-any-video", "style-sampling", "hyperframes"),
          ("reverse video", "reverse a video", "reverse engineer video", "reverse engineer a video", "video reverse engineering",
           "phân tích video mẫu", "phân tích video tham chiếu", "tái tạo video", "dựng lại video",
           "video dna", "复刻这个视频", "照着这个视频做一个")),
    Route(145, ("style-sampling", "reverse-any-video", "hyperframes"),
          ("style sampling", "theo phong cách", "in the style of", "sample this style", "an episode of",
           "用这个风格做一集")),
    Route(157, ("video-qc-auditor", "hyperframes", "media-use"),
          ("kiểm duyệt", "nghiệm thu video", "forensic qc", "qc video", "video qc", "quality control")),
    Route(120, ("video-qc-auditor", "hyperframes", "media-use"), ("qc", "forensic")),
    Route(139, ("figma", "hyperframes", "hyperframes-registry"), ("figma", "figma.com")),
    Route(140, ("slideshow", "hyperframes", "openai-pptx"),
          ("hyperframes slideshow", "hyperframes present", "presenter mode", "slideshow")),
    Route(145, ("remotion-to-hyperframes", "hyperframes", "remotion-best-practices"),
          ("remotion to hyperframes", "remotion sang hyperframes", "chuyển remotion", "port remotion")),
    Route(137, ("hyperframes-cli", "hyperframes", "hyperframes-registry"),
          ("hyperframes cli", "hyperframes check", "hyperframes render", "hyperframes preview")),
    Route(137, ("hyperframes-registry", "hyperframes", "hyperframes-cli"),
          ("hyperframes registry", "hyperframes add", "hyperframes catalog", "crt scanlines")),
    Route(102, ("hyperframes", "hyperframes-cli", "hyperframes-registry"),
          ("hyperframes", "html stage", "sân khấu html")),
    Route(130, ("media-use", "hyperframes", "video-qc-auditor"),
          ("micro sfx", "mix audio", "phối âm", "phối bgm", "audio ducking", "voiceover", "tactile sfx")),
    Route(134, ("remotion-captions", "remotion-best-practices", "remotion-markup"),
          ("remotion captions", "remotion subtitle", "phụ đề remotion")),
    Route(134, ("remotion-create", "remotion-best-practices", "remotion-studio"),
          ("remotion create", "new remotion", "tạo video remotion")),
    Route(134, ("remotion-docs", "remotion-best-practices", "remotion-markup"),
          ("remotion docs", "remotion documentation", "tài liệu remotion")),
    Route(134, ("remotion-interactivity", "remotion-saas", "remotion-best-practices"),
          ("remotion interactivity", "interactive remotion", "remotion player")),
    Route(134, ("remotion-license", "remotion-docs", "remotion-saas"),
          ("remotion license", "remotion pricing", "giấy phép remotion")),
    Route(134, ("remotion-maps", "remotion-markup", "remotion-best-practices"),
          ("remotion maps", "remotion map", "bản đồ remotion")),
    Route(134, ("remotion-markup", "remotion-best-practices", "remotion-studio"),
          ("remotion markup", "remotion effects", "remotion animation")),
    Route(134, ("remotion-multimedia", "remotion-render", "remotion-best-practices"),
          ("mediabunny", "remotion multimedia")),
    Route(134, ("remotion-render", "remotion-studio", "remotion-best-practices"),
          ("remotion render", "render remotion", "xuất video remotion")),
    Route(134, ("remotion-saas", "remotion-interactivity", "remotion-best-practices"),
          ("remotion saas", "app remotion")),
    Route(134, ("remotion-studio", "remotion-render", "remotion-best-practices"),
          ("remotion studio", "remotion preview", "xem trước remotion")),
    Route(134, ("remotion-upgrade", "remotion-docs", "remotion-best-practices"),
          ("remotion upgrade", "upgrade remotion", "nâng cấp remotion")),
    Route(100, ("remotion-best-practices", "remotion-create", "remotion-studio"), ("remotion",)),
)


# Những lệnh khởi động có sẵn và dùng được khi chưa có media đầu vào.
PYTHON_ENTRY_POINTS = {
    "agency-client-deliverables": ("build_agency_pack.py", "--self-test"),
    "an-vuong-daily-autopilot": ("avpm_autopilot_guard.py", "--self-test"),
    "capcut-pro-editor": ("capcut_draft_doctor_and_safezone.py", "--self-test"),
    "hyperframes": ("hyperframes_stage_auditor.py", "--self-test"),
    "kobe-motion-talking-head": ("plan_10_scripts_3hooks.py", "--topic", "Video tư vấn"),
    "media-use": ("studio_audio_sfx_mixer.py", "--self-test"),
    "openai-docx": ("heading_audit.py", "--help"),
    "phim-ai-flow-prompt": ("flow_storyboard_compiler.py", "--help"),
    "photoshop-pro-studio": ("ps2026_commercial_batch_studio.py", "--self-test"),
    "podcast-doanh-nhan-bds": ("podcast_bds_pack_builder.py", "--recommend-font-pair", "bds"),
    "premiere-pro-master-editor": ("premiere_xml_and_qc_bridge.py", "--self-test"),
    "remotion-to-hyperframes": ("lint_source.py", "--help"),
    "reverse-any-video": ("video_dna_reverse_engineer.py", "--self-test"),
    "talking-head-ngoi-ban": ("ngoi_ban_v6_validator_and_planner.py", "--episode", "1"),
    "talking-head-v3": ("talking_head_v3_master_pipeline.py", "--self-test"),
    "tvc-khong-gian-dich-vu": ("nvenc_lut_and_flash_sanitizer.py", "--self-test"),
    "video-qc-auditor": ("forensic_qc_analyzer.py", "--self-test"),
    "viet-han-video-ban-hang": ("master_ads_loudness_11lufs.py", "--help"),
}

AFTER_EFFECTS = Path("C:/Program Files/Adobe/Adobe After Effects 2027/Support Files/AfterFX.exe")


def find_skills_root() -> Path:
    here = Path(__file__).resolve().parent
    for directory in (here, *here.parents):
        if directory.name == SKILL_STORE.name and directory.parent.name == SKILL_STORE.parent.name:
            return directory
        candidate = directory / SKILL_STORE
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"Không tìm thấy {SKILL_STORE.as_posix()} từ {here}")


def read_frontmatter(guide: Path, yaml) -> tuple[str, str]:
    lines = guide.read_text(encoding="utf-8-sig").splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.rstrip() in {"---", "..."}:
                try:
                    data = yaml.safe_load("\n".join(lines[1:index]))
                except yaml.YAMLError as exc:
                    raise ValueError(f"YAML lỗi trong {guide}: {exc}") from exc
                if isinstance(data, dict) and all(
                    isinstance(data.get(key), str) and data[key].strip() for key in ("name", "description")
                ):
                    return data["name"].strip(), " ".join(data["description"].split())
                break
    raise ValueError(f"Frontmatter cần có name và description trong {guide}")


def list_tools(skill_dir: Path, subdir: str) -> tuple[str, ...]:
    tools = []
    for path in (skill_dir / subdir).rglob("*"):
        relative = path.relative_to(skill_dir)
        if path.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            tools.append(relative.as_posix())
    return tuple(sorted(tools, key=str.casefold))


def discover_skills(root: Path) -> dict[str, Skill]:
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("--list và --recommend cần thư viện PyYAML trong Python hiện tại.") from exc

    skills = {}
    for guide in sorted(root.glob("*/SKILL.md")):
        name, description = read_frontmatter(guide, yaml)
        skill = Skill(guide, name, description, list_tools(guide.parent, "scripts"),
                      list_tools(guide.parent, "templates"))
        skills[skill.slug] = skill
    if not skills:
        raise ValueError(f"Kho không có tệp SKILL.md: {root}")
    return skills


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold()).replace("đ", "d")
    accent_free = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"[^\W_]+", accent_free))


def recommend(skills: dict[str, Skill], request: str) -> list[tuple[Skill, tuple[str, ...]]]:
    normalized = normalize(request)
    search_text = f" {normalized} "
    # QC trong tên TVC QC sản phẩm là viết tắt của quảng cáo.
    qc_text = search_text.replace(" tvc qc san pham ", " tvc san pham ")
    matches: dict[str, dict[str, int]] = {}

    for route in ROUTES:
        keyword = max(
            (term for term in route.keywords if f" {normalize(term)} " in (qc_text if term == "qc" else search_text)),
            key=len,
            default=None,
        )
        if keyword is None:
            continue
        for slug, points in zip(route.skills, (route.priority, 62, 48)):
            if slug in skills:
                evidence = matches.setdefault(slug, {})
                evidence[keyword] = max(points, evidence.get(keyword, 0))

    for skill in skills.values():
        names = {normalize(skill.slug), normalize(skill.name)}
        explicit_id = re.search(rf"(?<![\w-]){re.escape(skill.slug)}(?![\w-])", request, re.IGNORECASE)
        if normalized in names or ("-" in skill.slug and explicit_id):
            matches.setdefault(skill.slug, {})[skill.slug] = 200

    def rank(slug: str) -> tuple[int, int, str]:
        scores = matches[slug].values()
        return -max(scores), -sum(scores), slug

    return [
        (skills[slug], tuple(sorted(matches[slug], key=matches[slug].get, reverse=True)))
        for slug in sorted(matches, key=rank)[:3]
    ]


def powershell_literal(value: str | Path) -> str:
    return "'" + re.sub(r"['\u2018\u2019]", lambda match: match[0] * 2, str(value)) + "'"


def command_for(skill: Skill, evidence: tuple[str, ...]) -> tuple[str, str]:
    entry = PYTHON_ENTRY_POINTS.get(skill.slug)
    if entry and f"scripts/{entry[0]}" in skill.scripts:
        script = skill.guide.parent / "scripts" / entry[0]
        args = " ".join(arg if arg.startswith("--") else powershell_literal(arg) for arg in entry[1:])
        label = {"--self-test": "Tự kiểm tra", "--help": "Xem cách dùng CLI"}.get(entry[1], "Chạy mẫu")
        return label, f"& {powershell_literal(sys.executable)} -X utf8 {powershell_literal(script)} {args}"

    jsx = "scripts/ae2027_luxury_tvc_builder.jsx"
    if (skill.slug == "tvc-qc-san-pham" and jsx in skill.scripts
            and any(keyword in AFTER_EFFECTS_KEYWORDS for keyword in evidence) and AFTER_EFFECTS.is_file()):
        return "Dựng composition trong project After Effects đang mở", (
            f"& {powershell_literal(AFTER_EFFECTS)} -r {powershell_literal(skill.guide.parent / jsx)}"
        )
    return "Mở hướng dẫn quy trình", f"Get-Content -LiteralPath {powershell_literal(skill.guide)} -Encoding UTF8"


def print_inventory(root: Path, skills: dict[str, Skill]) -> None:
    print(f"Kho Full Studio V6 · {len(skills)} kỹ năng · {root}")
    for skill in skills.values():
        label = skill.slug if skill.name == skill.slug else f"{skill.slug}  [{skill.name}]"
        print(f"\n{label}\n  {skill.description}")
        for folder, files in (("scripts", skill.scripts), ("templates", skill.templates)):
            print(f"  {folder}/ ({len(files)})")
            for file in files:
                print(f"    {file}")


def self_test(root: Path) -> int:
    sources = sorted(path for path in root.rglob("*.py") if path.is_file())
    if not sources:
        print(f"Không tìm thấy tệp Python trong {root}", file=sys.stderr)
        return 1

    failures = 0
    with tempfile.TemporaryDirectory(prefix="studio-skill-router-") as temporary:
        bytecode = str(Path(temporary) / "check.pyc")
        for source in sources:
            try:
                py_compile.compile(str(source), cfile=bytecode, doraise=True)
            except (OSError, py_compile.PyCompileError) as exc:
                failures += 1
                print(f"{source.relative_to(root)}\n{exc}", file=sys.stderr)

    print(f"py_compile: {len(sources) - failures}/{len(sources)} tệp Python đạt · {root}")
    if failures:
        return 1
    print("SELF_TEST_OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Điều phối kho kỹ năng Full Studio V6.")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--list", action="store_true", help="Liệt kê kỹ năng, scripts/ và templates/.")
    modes.add_argument("--recommend", metavar="YÊU_CẦU", help="Gợi ý tối đa 3 kỹ năng và lệnh PowerShell.")
    modes.add_argument("--self-test", action="store_true", help="Dùng py_compile kiểm toàn bộ tệp Python trong kho.")
    args = parser.parse_args(argv)

    try:
        root = find_skills_root()
        if args.self_test:
            return self_test(root)
        skills = discover_skills(root)
        if args.list:
            print_inventory(root, skills)
            return 0

        if not args.recommend.strip():
            parser.error("--recommend cần một yêu cầu có nội dung.")
        results = recommend(skills, args.recommend)
        if not results:
            print("Chưa tìm thấy kỹ năng phù hợp. Dùng --list để tra theo tên kỹ năng.")
        for index, (skill, evidence) in enumerate(results, start=1):
            label, command = command_for(skill, evidence)
            print(f"{index}. {skill.slug} · Khớp {', '.join(evidence)}")
            print(f"   {label}\n   {command}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
