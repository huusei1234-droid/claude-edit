"""Inspect HyperFrames stage HTML using only the Python standard library."""

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


PORTRAIT = (1080, 1920)
LANDSCAPE = (1920, 1080)
CAPTION_MIN_BOTTOM = 372
CAPTION_CLASSES = {"subtitle", "caption"}
STAGE_NAMES = {"root", "stage", "composition"}
STAGE_PROPERTIES = {"width", "height", "overflow", "overflow-x", "overflow-y"}

QUOTED = r""""(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'"""
CSS_COMMENTS = re.compile(rf"{QUOTED}|/\*.*?\*/", re.DOTALL)
CSS_TOKENS = re.compile(rf"{QUOTED}|\\.|[()\[\]{{}};,]", re.DOTALL)
JS_COMMENTS = re.compile(rf"{QUOTED}|`(?:\\.|[^`\\])*`|/\*.*?\*/|//[^\n]*", re.DOTALL)
JS_TIMELINE = re.compile(r"\bgsap\s*\.|\b__timelines\b")
JS_BLUR = re.compile(r"""\b(?:filter|backdropFilter)["']?\s*:\s*["'`][^"'`]*\bblur\s*\(""", re.I)
JS_SCALE = re.compile(r"\bscale(?:[XYZ])?[\"']?\s*:\s*[^\s,}]", re.I)
JS_EASE = re.compile(r"""\bease["']?\s*:\s*(?!["'`](?:none|linear|power0(?:\.\w+)?)["'`])(?:["'`][^"'`]+["'`]|[\w$(])""", re.I)
PIXELS = re.compile(r"([+-]?(?:\d+(?:\.\d+)?|\.\d+))(px)?", re.I)
DATA_DIMENSION = re.compile(r"0*(1080|1920)")
QUALIFIER = re.compile(rf"""([.#])([\w-]+)|\[\s*([\w-]+)(?:\s*=\s*({QUOTED}|[\w-]+))?\s*\]""")
SIMPLE_SELECTOR = re.compile(r"([a-zA-Z][\w-]*|\*)?(.*)", re.S)
SELECTOR_ARGUMENT = re.compile(rf"{QUOTED}|\[[^\]]*\]|\([^()]*\)")


@dataclass
class Declaration:
    name: str
    value: str
    line: int
    important: bool


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    line: int
    inline_style: list[Declaration]

    @property
    def classes(self):
        return set(self.attrs.get("class", "").split())


@dataclass
class Rule:
    selectors: list[str]
    declarations: list[Declaration]
    nested: bool


@dataclass
class Finding:
    level: str
    code: str
    message: str
    line: int = 1


class StageHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.styles = []
        self.scripts = []
        self.raw_tag = None
        self.capture_script = False

    def handle_starttag(self, tag, attrs):
        attributes = {name: value or "" for name, value in attrs}
        line = self.getpos()[0]
        if tag in {"style", "script"}:
            self.raw_tag = tag
            script_type = attributes.get("type", "").lower().strip()
            self.capture_script = script_type in {"", "module", "text/javascript", "application/javascript"}
        else:
            inline_style = hide_comments(CSS_COMMENTS, attributes.get("style", ""))
            self.elements.append(Element(tag, attributes, line, list(parse_declarations(inline_style, line))))

    def handle_endtag(self, tag):
        if tag == self.raw_tag:
            self.raw_tag = None

    def handle_data(self, data):
        if self.raw_tag == "style":
            self.styles.append((data, self.getpos()[0]))
        elif self.raw_tag == "script" and self.capture_script:
            self.scripts.append(data)


def hide_comments(pattern, source):
    def replace(match):
        value = match[0]
        if value.startswith("/"):
            return re.sub(r"[^\r\n]", " ", value)
        return value

    return pattern.sub(replace, source)


def css_delimiters(source, wanted):
    depth = 0
    for match in CSS_TOKENS.finditer(source):
        token = match[0]
        if token in {"(", "["}:
            depth += 1
        elif token in {")", "]"}:
            depth = max(0, depth - 1)
        elif not depth and token in wanted:
            yield match.start(), token


def parse_declarations(source, first_line):
    start = 0
    for end, _ in [*css_delimiters(source, {";"}), (len(source), "")]:
        chunk = source[start:end]
        name, colon, raw_value = chunk.partition(":")
        if colon and re.fullmatch(r"[\w-]+", name.strip()):
            important = re.search(r"!\s*important\s*$", raw_value, re.I)
            value = raw_value[:important.start()] if important else raw_value
            line = first_line + source.count("\n", 0, start + len(name) - len(name.lstrip()))
            yield Declaration(name.strip().lower(), value.strip(), line, bool(important))
        start = end + 1


def parse_rules(source, first_line):
    source = hide_comments(CSS_COMMENTS, source)
    blocks = []
    start = 0
    previous_open = -1
    for position, token in css_delimiters(source, {"{", "}", ";"}):
        if token == "{":
            blocks.append((source[start:position].strip(), position))
            previous_open = position
        if token == "}" and blocks:
            selector, opening = blocks.pop()
            if opening == previous_open:
                # A leaf block contains declarations. Wrapper blocks contain other rules.
                bounds = [-1, *(index for index, _ in css_delimiters(selector, {","})), len(selector)]
                selectors = [selector[left + 1:right].strip() for left, right in zip(bounds, bounds[1:])]
                declarations = list(parse_declarations(source[opening + 1:position],
                                                       first_line + source.count("\n", 0, opening)))
                yield Rule(selectors, declarations, bool(blocks))
        start = position + 1


def simple_specificity(selector, element):
    """Match a single CSS compound such as main#root[data-composition-id]."""
    if selector == ":root" and element.tag == "html":
        return (0, 0, 1, 0)
    tag, qualifiers = SIMPLE_SELECTOR.fullmatch(selector).groups()
    if not selector or (tag not in {None, "*"} and tag.lower() != element.tag):
        return None
    ids = classes = end = 0
    for token in QUALIFIER.finditer(qualifiers):
        marker, name, attribute, value = token.groups()
        if token.start() != end:
            return None
        end = token.end()
        if marker == "#":
            if name != element.attrs.get("id"):
                return None
            ids += 1
        else:
            if marker == "." and name not in element.classes:
                return None
            if attribute and (attribute not in element.attrs or
                              (value is not None and value.strip("\"'") != element.attrs[attribute])):
                return None
            classes += 1
    if end == len(qualifiers):
        return (0, ids, classes, int(tag not in {None, "*"}))
    return None


def stage_styles(element, rules):
    winners = {}

    def apply(declarations, specificity):
        for decl in declarations:
            if decl.name not in STAGE_PROPERTIES:
                continue
            rank = (decl.important, *specificity)
            names = ("overflow-x", "overflow-y") if decl.name == "overflow" else (decl.name,)
            values = decl.value.split() if len(names) == 2 else [decl.value]
            if 1 <= len(values) <= len(names):
                for index, name in enumerate(names):
                    if name not in winners or rank >= winners[name][0]:
                        winners[name] = (rank, values[min(index, len(values) - 1)].lower())

    for rule in rules:
        if rule.nested:
            continue
        matches = (simple_specificity(selector, element) for selector in rule.selectors)
        specificity = max((match for match in matches if match is not None), default=None)
        if specificity is not None:
            apply(rule.declarations, specificity)
    apply(element.inline_style, (1, 0, 0, 0))
    return {name: value for name, (_, value) in winners.items()}


def pixels(value):
    match = PIXELS.fullmatch(value)
    if match:
        number = float(match[1])
        if match[2] or number == 0:
            return number
    return None


def find_stage(elements, rules):
    fallback = None
    for element in elements:
        if "data-composition-id" in element.attrs or {"data-width", "data-height"} <= element.attrs.keys():
            return element, stage_styles(element, rules)
        if element.attrs.get("id") in STAGE_NAMES or element.classes & STAGE_NAMES:
            styles = stage_styles(element, rules)
            if all(pixels(styles.get(name, "")) is not None for name in ("width", "height")):
                return element, styles
            if fallback is None:
                fallback = (element, styles)

    for element in elements:
        if element.tag in {"main", "body", "html"}:
            styles = stage_styles(element, rules)
            if all(pixels(styles.get(name, "")) is not None for name in ("width", "height")):
                return element, styles
    return fallback or (None, {})


def motion_signals(declarations, scripts):
    css = [(decl.name, decl.value.lower()) for decl in declarations]
    js = "\n".join(hide_comments(JS_COMMENTS, script) for script in scripts)
    gsap = js if JS_TIMELINE.search(js) else ""
    return {
        "blur": any(name.endswith("filter") and re.search(r"\bblur\s*\(", value) for name, value in css)
        or bool(JS_BLUR.search(gsap)),
        "scale": any((name == "scale" and value not in {"", "none"}) or
                     (name.endswith("transform") and re.search(r"\bscale(?:[xyz]|3d)?\s*\(", value))
                     for name, value in css) or bool(JS_SCALE.search(gsap)),
        "cubic-bezier / GSAP ease": any(re.search(r"\bcubic-bezier\s*\(", value) for _, value in css)
        or bool(JS_EASE.search(gsap)),
    }


def caption_subject(selector, caption_ids):
    subject = re.split(r"[\s>+~]+", SELECTOR_ARGUMENT.sub("", selector).strip())[-1]
    return (set(re.findall(r"\.([\w-]+)", subject)) & CAPTION_CLASSES
            or set(re.findall(r"#([\w-]+)", subject)) & caption_ids)


def caption_findings(elements, rules):
    captions = [element for element in elements if element.classes & CAPTION_CLASSES]
    caption_ids = {element.attrs["id"] for element in captions if "id" in element.attrs}
    targets = [(element.attrs["class"], element.inline_style) for element in captions]
    for rule in rules:
        selectors = [selector for selector in rule.selectors if caption_subject(selector, caption_ids)]
        if selectors:
            targets.append((", ".join(selectors), rule.declarations))
    for target, declarations in targets:
        for decl in declarations:
            bottom = pixels(decl.value) if decl.name == "bottom" else None
            if bottom is not None and bottom < CAPTION_MIN_BOTTOM:
                yield Finding("WARN", "CAPTION_BOTTOM",
                              f"{target} dùng bottom {decl.value}. "
                              f"Safe zone TikTok/Reels cần bottom ≥ {CAPTION_MIN_BOTTOM}px.", decl.line)


def audit_html(source, *, stages_only=False):
    page = StageHTML()
    page.feed(source)
    page.close()
    rules = [rule for css, line in page.styles for rule in parse_rules(css, line)]
    stage, styles = find_stage(page.elements, rules)
    css_size = tuple(pixels(styles.get(name, "")) for name in ("width", "height"))
    attrs = stage.attrs if stage else {}
    data_size = tuple(attrs.get(name, "").strip() for name in ("data-width", "data-height"))
    declared_stage = "data-composition-id" in attrs or any(data_size) or all(value is not None for value in css_size)
    placeholder = data_size == ("0", "0") and css_size == (None, None)
    if stages_only and (not declared_stage or placeholder):
        return None

    findings = []
    line = stage.line if stage else 1
    size = css_size
    if any(data_size):
        dimensions = [DATA_DIMENSION.fullmatch(value) for value in data_size]
        size = tuple(int(match[1]) if match else None for match in dimensions)
    if size not in {PORTRAIT, LANDSCAPE}:
        findings.append(Finding("ERROR", "STAGE_SIZE", "Cần khai báo chiều rộng × chiều cao sân khấu 1080×1920 hoặc 1920×1080.", line))
    elif any(data_size) and any(css is not None and css != declared for css, declared in zip(css_size, size)):
        findings.append(Finding("ERROR", "STAGE_SIZE", "Kích thước px trong CSS khác data-width/data-height của sân khấu.", line))
    if (styles.get("overflow-x"), styles.get("overflow-y")) != ("hidden", "hidden"):
        findings.append(Finding("ERROR", "STAGE_OVERFLOW", "Cần overflow: hidden trên phần tử sân khấu cho cả hai trục.", line))

    declarations = [decl for rule in rules for decl in rule.declarations]
    declarations.extend(decl for element in page.elements for decl in element.inline_style)
    missing = [signal for signal, present in motion_signals(declarations, page.scripts).items() if not present]
    if missing:
        findings.append(Finding("WARN", "MOTION_SIGNALS", f"Thiếu dấu hiệu chuyển động trong mã tĩnh ({', '.join(missing)}).", line))
    if size == PORTRAIT:
        findings.extend(caption_findings(page.elements, rules))
    return findings


def audit_file(path, *, stages_only=False):
    try:
        return audit_html(path.read_text(encoding="utf-8-sig"), stages_only=stages_only)
    except (OSError, UnicodeError) as error:
        return [Finding("ERROR", "READ_HTML", str(error))]


def report(path, findings):
    if not findings:
        print(f"{path} PASS")
    for finding in findings:
        print(f"{path}:{finding.line}: {finding.level} [{finding.code}] {finding.message}")


def self_test():
    html = """
    <template>
      <style>
        #root { overflow: hidden }
        .card { filter: blur(14px); transform: scale(.94) }
        .subtitle, .caption { position: fixed; bottom: 372px }
        .caption-icon { bottom: 0 }
        .caption .sparkle { bottom: 0 }
      </style>
      <main id="root" data-composition-id="v6" data-width="1080" data-height="1920">
        <p class="caption">Phụ đề tiếng Việt</p><span style="bottom: 0"></span>
      </main>
      <script>gsap.timeline({paused: true}).to('.card', {ease: 'power2.out'});</script>
    </template>
    """
    unsafe = html.replace("372px", "371.5px !important")
    landscape = unsafe.replace('data-width="1080" data-height="1920"', 'data-width="1920" data-height="1080"')
    css_stage = html.replace('data-composition-id="v6" data-width="1080" data-height="1920"', "").replace(
        "overflow: hidden", "width: 1080px; height: 1920px; overflow: hidden"
    )
    cases = [
        ("mép an toàn 372px", html, []),
        ("phụ đề vào đáy cấm", unsafe, [("WARN", "CAPTION_BOTTOM")]),
        ("inline bottom 0", html.replace('class="caption"', 'class="caption" style="bottom: 0"'),
         [("WARN", "CAPTION_BOTTOM")]),
        ("bottom trong media query", html.replace(".caption-icon { bottom: 0 }",
                                                  "@media (orientation: portrait) { .subtitle { bottom: 370px } }"),
         [("WARN", "CAPTION_BOTTOM")]),
        ("khung ngang", landscape, []),
        ("kích thước CSS", css_stage, []),
        ("sân khấu CSS chứa composition con",
         '<body style="width: 100%; height: 100%">'
         + css_stage.replace("</main>", '<div data-composition-id="child" data-width="400" data-height="200"></div></main>')
         + "</body>", []),
        ("sai kích thước và overflow", html.replace('data-width="1080"', 'data-width="720"').replace(
            "overflow: hidden", "overflow: hidden; overflow-y: visible"),
         [("ERROR", "STAGE_SIZE"), ("ERROR", "STAGE_OVERFLOW")]),
        ("GSAP blur và scale", html.replace(".card { filter: blur(14px); transform: scale(.94) }", "").replace(
            "ease: 'power2.out'", "filter: 'blur(0px)', scaleY: 1, ease: 'power2.out'"), []),
        ("CSS cubic-bezier", html.replace("ease: 'power2.out'", "ease: 'none'").replace(
            "transform: scale(.94)", "transform: scale(.94); transition: transform .3s cubic-bezier(.2, .8, .2, 1)"), []),
        ("ease tuyến tính", html.replace("ease: 'power2.out'", "ease: 'none'"), [("WARN", "MOTION_SIGNALS")]),
    ]
    for name, source, wanted in cases:
        actual = [(finding.level, finding.code) for finding in audit_html(source)]
        if actual != wanted:
            raise AssertionError(f"{name}: expected {wanted}, got {actual}")
    print("SELF_TEST_OK")


def main(argv=None):
    parser = argparse.ArgumentParser(description="HyperFrames V6 Safe-Zone & Physics Inspector (kiểm tra tĩnh).")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--html", type=Path, metavar="STAGE.HTML", help="Kiểm tra một sân khấu HTML.")
    mode.add_argument("--audit-all", type=Path, metavar="SKILLS_ROOT", help="Quét đệ quy các sân khấu HTML trong thư mục.")
    mode.add_argument("--self-test", action="store_true", help="Chạy các ca kiểm thử HTML tích hợp.")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        return 0
    if args.html is not None:
        findings = audit_file(args.html)
        report(args.html, findings)
        return int(any(finding.level == "ERROR" for finding in findings))

    root = args.audit_all
    if not root.is_dir():
        parser.error(f"Thư mục không tồn tại hoặc không đọc được ({root}).")
    checked = skipped = errors = warnings = 0
    for path in sorted(root.rglob("*.html")):
        if not path.is_file():
            continue
        findings = audit_file(path, stages_only=True)
        if findings is None:
            skipped += 1
            continue
        checked += 1
        report(path.relative_to(root), findings)
        errors += sum(finding.level == "ERROR" for finding in findings)
        warnings += sum(finding.level == "WARN" for finding in findings)
    print(f"AUDIT_SUMMARY stages={checked} skipped={skipped} errors={errors} warnings={warnings}")
    if not checked:
        print(f"Không tìm thấy sân khấu HTML trong {root}.", file=sys.stderr)
    return int(bool(errors) or not checked)


if __name__ == "__main__":
    sys.exit(main())
