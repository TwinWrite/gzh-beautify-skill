#!/usr/bin/env python3
"""Lint a produced theme package (theme.json + THEME.md + preview.html)."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REQUIRED_SLOTS = [
    "root",
    "hero",
    "toc",
    "h2",
    "h3",
    "h3_label",
    "paragraph",
    "divider",
    "strong",
    "mark",
    "underline",
    "strike",
    "code_inline",
    "blockquote",
    "callout_tip",
    "callout_warn",
    "quote_pull",
    "ul",
    "ol",
    "table",
    "code_dark",
    "code_light",
    "image",
    "image_gif",
    "media_ph",
    "footer",
]

REQUIRED_MD_HEADINGS = [
    "## 结构模型",
    "## 设计变量",
    "## 必选槽",
    "## 签名槽",
    "## 文章骨架",
    "## 文章类型配方",
    "## Markdown 映射",
]

ARTICLE_TYPES = [
    "tutorial",
    "listicle",
    "opinion",
    "interview",
    "report",
    "essay",
    "case",
]

HTML_FENCE = re.compile(r"```html\s*\n(.*?)```", re.S)
SLOT_HEADING = re.compile(r"^### slot:([a-z][a-z0-9_]*)\s*$", re.M)
SIG_HEADING = re.compile(r"^### sig:([a-z][a-z0-9-]*)\s*$", re.M)
COMPONENT_HEADING = re.compile(r"^### (slot|sig):([a-z][a-z0-9_-]*)\s*$", re.M)
FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
FOURSIDE_DASHED = re.compile(r"border\s*:\s*[^;{}]*dashed", re.I)
CENTERED = re.compile(r"text-align\s*:\s*center", re.I)
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,38}[a-z0-9]$")
CJK = re.compile(r"[一-鿿㐀-䶿]")
PLACEHOLDER = re.compile(r"\{\{[a-z0-9_]+\}\}", re.I)
SCHEME_IGNORED = re.compile(r"[\x00-\x20\x7f]+")
PREVIEW_ID_TAIL = re.compile(r"[a-z0-9_-]")
RECIPE_LIST = re.compile(r"^(?:[-*+]|\d+\.)\s+`?([a-z][a-z0-9_-]*)`?", re.I)
EXEC_SCHEME = re.compile(
    r"^\s*(?:javascript|vbscript|livescript|mocha)\s*:|"
    r"^\s*data\s*:\s*(?:text\s*/\s*html|text\s*/\s*javascript|application\s*/\s*(?:javascript|ecmascript))",
    re.I,
)
EXEC_IN_STYLE = re.compile(r"javascript\s*:|expression\s*\(|-moz-binding", re.I)

SKIP_TAGS = {"head", "title", "style", "script"}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
URL_ATTRS = {
    "href",
    "src",
    "xlink:href",
    "action",
    "formaction",
    "poster",
    "cite",
    "background",
    "data",
    "dynsrc",
    "lowsrc",
}
FORBIDDEN_THEME_TAGS = {
    "div": "出现 <div>，请用 <section>",
    "style": "出现 <style>",
    "script": "出现 <script>",
    "svg": "出现禁止标签",
    "canvas": "出现禁止标签",
    "video": "出现禁止标签",
    "audio": "出现禁止标签",
    "iframe": "出现禁止标签",
    "form": "出现禁止标签",
    "button": "出现禁止标签",
    "input": "出现禁止标签",
    "pre": "禁止 <pre>/<code>，代码块请逐行 <p>",
    "code": "禁止 <pre>/<code>，代码块请逐行 <p>",
}
THEME_STYLE_CHECKS = [
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "禁止 position fixed/absolute/sticky"),
    (re.compile(r"float\s*:", re.I), "禁止 float"),
    (re.compile(r"display\s*:\s*grid", re.I), "禁止 display:grid"),
    (re.compile(r"var\s*\(\s*--", re.I), "禁止 CSS 变量"),
    (re.compile(r"@(media|keyframes|import)", re.I), "禁止 @media/@keyframes/@import"),
    (re.compile(r"white-space\s*:\s*pre", re.I), "禁止 white-space:pre，代码块请逐行 <p>"),
]


def _srgb(channel: float) -> float:
    channel = channel / 255.0
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    raw = hex_color.lstrip("#")
    r = int(raw[0:2], 16)
    g = int(raw[2:4], 16)
    b = int(raw[4:6], 16)
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def contrast_ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def load_schema(skill_root: Path) -> dict:
    path = skill_root / "references" / "theme.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_ref(schema: dict, node: dict) -> dict:
    ref = node.get("$ref")
    if not ref:
        return node
    if not ref.startswith("#/$defs/"):
        raise ValueError(f"unsupported $ref: {ref}")
    return schema["$defs"][ref.split("/")[-1]]


def validate_against_schema(instance, schema: dict, node: dict | None = None, path: str = "$") -> list[str]:
    node = _resolve_ref(schema, schema if node is None else node)
    errors: list[str] = []
    expected = node.get("type")
    if expected == "object":
        if not isinstance(instance, dict):
            return [f"{path}: 应为 object"]
        for key in node.get("required", []):
            if key not in instance:
                errors.append(f"{path}: 缺少字段 {key}")
        if node.get("additionalProperties") is False:
            allowed = set(node.get("properties", {}))
            for key in instance:
                if key not in allowed:
                    errors.append(f"{path}: 未知字段 {key}")
        for key, sub in node.get("properties", {}).items():
            if key in instance:
                errors.extend(validate_against_schema(instance[key], schema, sub, f"{path}.{key}"))
        return errors
    if expected == "array":
        if not isinstance(instance, list):
            return [f"{path}: 应为 array"]
        if "minItems" in node and len(instance) < node["minItems"]:
            errors.append(f"{path}: 至少 {node['minItems']} 项")
        if "maxItems" in node and len(instance) > node["maxItems"]:
            errors.append(f"{path}: 至多 {node['maxItems']} 项")
        if node.get("uniqueItems"):
            serialized = [
                json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item, (dict, list)) else item
                for item in instance
            ]
            if len(serialized) != len(set(serialized)):
                errors.append(f"{path}: 含重复项")
        item_schema = node.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate_against_schema(item, schema, item_schema, f"{path}[{i}]"))
        return errors
    if expected == "string":
        if not isinstance(instance, str):
            return [f"{path}: 应为 string"]
        if "minLength" in node and len(instance) < node["minLength"]:
            errors.append(f"{path}: 长度过短")
        if "maxLength" in node and len(instance) > node["maxLength"]:
            errors.append(f"{path}: 长度过长")
        if "pattern" in node and not re.search(node["pattern"], instance):
            errors.append(f"{path}: 不符合 pattern {node['pattern']}")
        if "enum" in node and instance not in node["enum"]:
            errors.append(f"{path}: 不在枚举 {node['enum']}")
        if "const" in node and instance != node["const"]:
            errors.append(f"{path}: 应为 {node['const']}")
        return errors
    if expected == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            return [f"{path}: 应为 integer"]
        if "minimum" in node and instance < node["minimum"]:
            errors.append(f"{path}: 小于 {node['minimum']}")
        return errors
    return errors


def find_theme_dirs(target: Path) -> list[Path]:
    if (target / "theme.json").is_file():
        return [target]
    dirs: list[Path] = []
    if target.is_dir():
        for child in sorted(target.iterdir()):
            if child.is_dir() and (child / "theme.json").is_file():
                dirs.append(child)
    return dirs


def is_executable_url(value: str) -> bool:
    if not value:
        return False
    return bool(EXEC_SCHEME.search(SCHEME_IGNORED.sub("", value)))


def attr_values(attrs, name: str) -> list[str]:
    lname = name.lower()
    return [(value or "") for key, value in attrs if key.lower() == lname]


def _duplicates(items: list[str]) -> list[str]:
    return sorted({item for item in items if items.count(item) > 1})


def recipe_entry_ids(section: str) -> set[str]:
    found: set[str] = set()
    for raw in section.splitlines():
        line = raw.strip()
        listed = RECIPE_LIST.match(line)
        if listed:
            found.add(listed.group(1).lower())
            continue
        if line.startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if cells and re.fullmatch(r"[a-z][a-z0-9_-]*", cells[0], re.I):
                found.add(cells[0].lower())
    return found


def has_preview_marker(preview: str, ident: str, *prefixes: str) -> bool:
    for prefix in prefixes:
        needle = f"{prefix}{ident}"
        start = 0
        while True:
            idx = preview.find(needle, start)
            if idx == -1:
                break
            end = idx + len(needle)
            if end == len(preview) or not PREVIEW_ID_TAIL.match(preview[end]):
                return True
            start = idx + 1
    return False


def _md_section(md_text: str, heading: str) -> str | None:
    start = md_text.find(heading)
    if start == -1:
        return None
    rest = md_text[start + len(heading) :]
    nxt = re.search(r"\n## ", rest)
    if nxt:
        return md_text[start : start + len(heading) + nxt.start()]
    return md_text[start:]


def iter_component_regions(md_text: str):
    headings = list(COMPONENT_HEADING.finditer(md_text))
    for i, match in enumerate(headings):
        region_start = match.end()
        region_end = headings[i + 1].start() if i + 1 < len(headings) else len(md_text)
        h2 = re.search(r"\n## ", md_text[region_start:region_end])
        if h2:
            region_end = region_start + h2.start()
        yield match.group(0).strip(), match.group(1), match.group(2), md_text[region_start:region_end]


class ThemeHtmlInspector(HTMLParser):
    def __init__(self, label: str) -> None:
        super().__init__(convert_charrefs=True)
        self.label = label
        self.stack: list[tuple[str, bool]] = []
        self.leaf_depth = 0
        self.findings: list[tuple[str, str]] = []
        self._seen: set[tuple[str, str]] = set()
        self._has_dashed = False
        self._has_center = False

    def _add(self, level: str, msg: str) -> None:
        item = (level, msg)
        if item in self._seen:
            return
        self._seen.add(item)
        self.findings.append(item)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._open(tag, attrs, void=True)

    def handle_starttag(self, tag: str, attrs) -> None:
        self._open(tag, attrs, void=tag in VOID_TAGS)

    def _open(self, tag: str, attrs, *, void: bool) -> None:
        ltag = tag.lower()
        ad = {k.lower(): v for k, v in attrs}
        if ltag in FORBIDDEN_THEME_TAGS:
            self._add("ERROR", f"{self.label}: {FORBIDDEN_THEME_TAGS[ltag]}")
        if "class" in ad:
            self._add("ERROR", f"{self.label}: 出现 class（交付组件禁止）")
        if "id" in ad:
            self._add("ERROR", f"{self.label}: 出现 id（THEME.md 组件禁止，预览页可用）")
        for name, value in attrs:
            lname = name.lower()
            if lname.startswith("on") and len(lname) > 2:
                self._add("ERROR", f"{self.label}: 禁止事件属性 {lname}")
            if lname in URL_ATTRS and is_executable_url(value or ""):
                self._add("ERROR", f"{self.label}: 禁止可执行 URL")
        for style in attr_values(attrs, "style"):
            normalized = SCHEME_IGNORED.sub("", style)
            if style and (EXEC_IN_STYLE.search(style) or EXEC_IN_STYLE.search(normalized)):
                self._add("ERROR", f"{self.label}: style 含可执行内容")
            for rx, msg in THEME_STYLE_CHECKS:
                if rx.search(style):
                    self._add("ERROR", f"{self.label}: {msg}")
            for size in FONT_SIZE.findall(style):
                if float(size) > 24:
                    self._add("ERROR", f"{self.label}: font-size {size}px 超过 24px")
            if FOURSIDE_DASHED.search(style):
                self._has_dashed = True
            if CENTERED.search(style):
                self._has_center = True
        is_leaf = ltag == "span" and "leaf" in ad
        if is_leaf:
            self.leaf_depth += 1
        if not void:
            self.stack.append((ltag, is_leaf))

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == ltag:
                for _, was_leaf in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if any(t in SKIP_TAGS for t, _ in self.stack):
            return
        if self.leaf_depth > 0:
            return
        text = data.strip()
        if not text:
            return
        if CJK.search(text) or PLACEHOLDER.search(text):
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self._add("ERROR", f"{self.label}: 占位或中文未包在 span[leaf] 内（{snippet}）")


def lint_html_block(html: str, label: str) -> list[tuple[str, str]]:
    inspector = ThemeHtmlInspector(label)
    try:
        inspector.feed(html)
        inspector.close()
    except Exception as exc:  # noqa: BLE001
        return [("WARN", f"{label}: HTML 解析中断: {exc}")]
    if inspector._has_dashed and not inspector._has_center:
        inspector._add("WARN", f"{label}: 四周虚线框，正文强调请改用竖条/标签")
    return inspector.findings


def lint_theme(theme_dir: Path, schema: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    json_path = theme_dir / "theme.json"
    md_path = theme_dir / "THEME.md"
    preview_path = theme_dir / "preview.html"

    if not json_path.is_file():
        return [f"{theme_dir}: 缺少 theme.json"], []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{json_path}: JSON 无法解析（{exc}）"], []

    for msg in validate_against_schema(data, schema):
        errors.append(f"{json_path.name}: {msg}")

    theme_id = data.get("id")
    if isinstance(theme_id, str):
        if theme_dir.name != theme_id:
            errors.append(f"目录名 {theme_dir.name} 与 id {theme_id} 不一致")
        if not ID_RE.match(theme_id):
            errors.append(f"id 非法: {theme_id}")

    color = (data.get("tokens") or {}).get("color") or {}
    if isinstance(color, dict) and all(isinstance(color.get(k), str) and HEX.match(color[k]) for k in ("page", "ink", "ink_muted", "brand_soft", "brand_ink")):
        page, ink, muted = color["page"], color["ink"], color["ink_muted"]
        if contrast_ratio(ink, page) < 7.0:
            errors.append(f"正文对比度不足: ink {ink} on page {page} < 7.0")
        if contrast_ratio(muted, page) < 4.5:
            errors.append(f"次要文字对比度不足: ink_muted on page < 4.5")
        if contrast_ratio(color["brand_ink"], color["brand_soft"]) < 4.5:
            errors.append("brand_ink 在 brand_soft 上对比度 < 4.5")
        if luminance(page) < 0.92:
            warnings.append("page 不是近白底；除非 brief 明确要求深色氛围，请改回浅底")

    underline_css = data.get("underline_css", "")
    if isinstance(color, dict) and isinstance(underline_css, str) and color.get("underline"):
        if color["underline"].lower() not in underline_css.lower():
            warnings.append("underline_css 未包含 tokens.color.underline")

    declared_slots = data.get("slots") if isinstance(data.get("slots"), list) else []
    missing_declared = [s for s in REQUIRED_SLOTS if s not in declared_slots]
    extra_declared = [s for s in declared_slots if s not in REQUIRED_SLOTS]
    if missing_declared:
        errors.append(f"theme.json slots 缺少: {', '.join(missing_declared)}")
    if extra_declared:
        errors.append(f"theme.json slots 含未知必选槽: {', '.join(extra_declared)}")

    unique_sigs: list[str] = []
    raw_sigs = data.get("signature_slots")
    if not isinstance(raw_sigs, list):
        errors.append("theme.json 缺少 signature_slots")
        sigs: list[str] = []
    else:
        sigs = [s for s in raw_sigs if isinstance(s, str)]
        unique_sigs = list(dict.fromkeys(sigs))
        dup_sigs = _duplicates(sigs)
        if dup_sigs:
            errors.append(f"theme.json signature_slots 重复: {', '.join(dup_sigs)}")
        if len(unique_sigs) < 8 or len(unique_sigs) > 16:
            errors.append(f"signature_slots 必须 8–16 个不重复 id，当前 {len(unique_sigs)}")

    if not md_path.is_file():
        errors.append("缺少 THEME.md")
        md_text = ""
    else:
        md_text = md_path.read_text(encoding="utf-8")
        for heading in REQUIRED_MD_HEADINGS:
            if heading not in md_text:
                errors.append(f"THEME.md 缺少章节 {heading}")
        recipe = _md_section(md_text, "## 文章类型配方")
        if recipe is not None:
            covered = recipe_entry_ids(recipe)
            for kind in ARTICLE_TYPES:
                if kind not in covered:
                    errors.append(f"THEME.md 文章类型配方缺少 {kind}")

        slot_ids = SLOT_HEADING.findall(md_text)
        for required in REQUIRED_SLOTS:
            if required not in slot_ids:
                errors.append(f"THEME.md 缺少 ### slot:{required}")
        dup = _duplicates(slot_ids)
        if dup:
            errors.append(f"THEME.md 重复槽: {', '.join(dup)}")

        sig_ids = SIG_HEADING.findall(md_text)
        unique_sig_ids = list(dict.fromkeys(sig_ids))
        sig_dup = _duplicates(sig_ids)
        if sig_dup:
            errors.append(f"THEME.md 重复签名槽: {', '.join(sig_dup)}")
        if len(unique_sig_ids) < 8 or len(unique_sig_ids) > 16:
            errors.append(f"THEME.md 签名槽必须 8–16 个不重复 id，当前 {len(unique_sig_ids)}")
        if sorted(unique_sigs) != sorted(unique_sig_ids):
            errors.append("theme.json signature_slots 与 THEME.md ### sig:* 不一致")

        for label, _kind, _ident, region in iter_component_regions(md_text):
            fences = list(HTML_FENCE.finditer(region))
            if not fences:
                errors.append(f"{label} 缺少 html 代码块")
                continue
            if len(fences) > 1:
                errors.append(f"{label} 应恰好一个 html 代码块，当前 {len(fences)}")
            for fence in fences:
                for level, msg in lint_html_block(fence.group(1), label):
                    (errors if level == "ERROR" else warnings).append(msg)

    if not preview_path.is_file():
        errors.append("缺少 preview.html")
    else:
        preview = preview_path.read_text(encoding="utf-8")
        if "<html" not in preview.lower():
            warnings.append("preview.html 不像完整 HTML 文档")
        for slot in REQUIRED_SLOTS:
            if not has_preview_marker(preview, slot, "slot:", "preview-slot-"):
                errors.append(f"preview.html 未展示 slot:{slot}")
        for sig in unique_sigs:
            if not has_preview_marker(preview, sig, "sig:", "preview-sig-", "preview-slot-"):
                errors.append(f"preview.html 未展示 sig:{sig}")

    return errors, warnings


def report(theme_dir: Path, errors: list[str], warnings: list[str]) -> None:
    print(f"── {theme_dir} ──")
    if not errors and not warnings:
        print("  OK")
        return
    for msg in errors:
        print(f"  ERROR  {msg}")
    for msg in warnings:
        print(f"  WARN   {msg}")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    skill_root = Path(__file__).resolve().parent.parent
    target = Path(argv[0]).resolve() if argv else (Path.cwd() / "themes")
    if not target.exists():
        print(f"找不到路径: {target}")
        return 1

    schema = load_schema(skill_root)
    dirs = find_theme_dirs(target)
    if not dirs:
        print(f"未发现主题包（需要 theme.json）: {target}")
        print("这是主题工厂，空目录是允许的。生产主题后再跑 lint。")
        return 0

    print(f"检查 {len(dirs)} 个主题包\n")
    total_err = total_warn = 0
    for theme_dir in dirs:
        errors, warnings = lint_theme(theme_dir, schema)
        report(theme_dir, errors, warnings)
        total_err += len(errors)
        total_warn += len(warnings)

    print(f"\n汇总: ERROR×{total_err}  WARN×{total_warn}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main())
