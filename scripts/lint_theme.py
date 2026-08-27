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
PLACEHOLDER = re.compile(r"\{\{")
SCHEME_IGNORED = re.compile(r"[\x00-\x20\x7f]+")
PREVIEW_ID_TAIL = re.compile(r"[a-zA-Z0-9_-]")
RECIPE_LIST = re.compile(r"^(?:[-*+]|\d+[.)])\s+`?([a-z][a-z0-9_-]*)`?\s*[:：]\s*(\S.*)$", re.I)
RECIPE_PLAIN = re.compile(r"^`?([a-z][a-z0-9_-]*)`?\s*[:：]\s*(\S.*)$", re.I)
RECIPE_SLOT = re.compile(
    r"(?<![a-z0-9_-])(?:" + "|".join(re.escape(s) for s in REQUIRED_SLOTS) + r")(?![a-z0-9_-])",
    re.I,
)
RECIPE_SIG = re.compile(r"(?:sig:|sig-)[a-z0-9-]+", re.I)
RECIPE_EXCLUDE_VERB = re.compile(r"不要用|排除|不用")
HTML_ATTR_NAME = re.compile(r"[A-Za-z_:][A-Za-z0-9_.:-]*")
EXEC_SCHEME = re.compile(
    r"^\s*(?:javascript|vbscript|livescript|mocha)\s*:|"
    r"^\s*data\s*:\s*(?:text\s*/\s*html|text\s*/\s*javascript|application\s*/\s*(?:javascript|ecmascript))",
    re.I,
)
EXEC_IN_STYLE = re.compile(r"javascript\s*:|expression\s*\(|-moz-binding", re.I)

SKIP_TAGS = {"head", "title", "style", "script"}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr", "param"}
HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
CSS_IMPORTANT = re.compile(r"!\s*important\s*$", re.I)
_CSS_DISPLAY_OK = frozenset({
    "none",
    "inline",
    "block",
    "inline-block",
    "flex",
    "inline-flex",
    "grid",
    "inline-grid",
    "flow-root",
    "contents",
    "list-item",
    "table",
    "inline-table",
    "table-row",
    "table-cell",
    "table-column",
    "table-column-group",
    "table-header-group",
    "table-footer-group",
    "table-row-group",
    "table-caption",
    "run-in",
    "-webkit-box",
    "-webkit-flex",
    "inherit",
    "initial",
    "unset",
    "revert",
    "revert-layer",
})
_CSS_VIS_OK = frozenset({
    "visible",
    "hidden",
    "collapse",
    "inherit",
    "initial",
    "unset",
    "revert",
    "revert-layer",
})
CSS_KNOWN_PROPS = frozenset({
    "accent-color", "align-content", "align-items", "align-self", "all",
    "animation", "appearance", "aspect-ratio", "background", "background-attachment",
    "background-clip", "background-color", "background-image", "background-origin",
    "background-position", "background-repeat", "background-size", "border",
    "border-bottom", "border-bottom-color", "border-bottom-left-radius",
    "border-bottom-right-radius", "border-bottom-style", "border-bottom-width",
    "border-collapse", "border-color", "border-image", "border-left",
    "border-left-color", "border-left-style", "border-left-width", "border-radius",
    "border-right", "border-right-color", "border-right-style", "border-right-width",
    "border-spacing", "border-style", "border-top", "border-top-color",
    "border-top-left-radius", "border-top-right-radius", "border-top-style",
    "border-top-width", "border-width", "bottom", "box-decoration-break",
    "box-shadow", "box-sizing", "break-after", "break-before", "break-inside",
    "caption-side", "caret-color", "clear", "clip", "clip-path", "color",
    "column-count", "column-gap", "column-rule", "column-span", "column-width",
    "columns", "contain", "content", "cursor", "direction", "display",
    "empty-cells", "filter", "flex", "flex-basis", "flex-direction", "flex-flow",
    "flex-grow", "flex-shrink", "flex-wrap", "float", "font", "font-family",
    "font-feature-settings", "font-kerning", "font-size", "font-size-adjust",
    "font-stretch", "font-style", "font-variant", "font-variation-settings",
    "font-weight", "gap", "grid", "grid-area", "grid-auto-columns", "grid-auto-flow",
    "grid-auto-rows", "grid-column", "grid-row", "grid-template",
    "grid-template-areas", "grid-template-columns", "grid-template-rows", "height",
    "hyphens", "inset", "isolation", "justify-content", "justify-items",
    "justify-self", "left", "letter-spacing", "line-break", "line-height",
    "list-style", "list-style-image", "list-style-position", "list-style-type",
    "margin", "margin-bottom", "margin-left", "margin-right", "margin-top",
    "mask", "max-height", "max-width", "min-height", "min-width", "mix-blend-mode",
    "object-fit", "object-position", "opacity", "order", "outline", "outline-color",
    "outline-offset", "outline-style", "outline-width", "overflow", "overflow-wrap",
    "overflow-x", "overflow-y", "padding", "padding-bottom", "padding-left",
    "padding-right", "padding-top", "place-content", "place-items", "place-self",
    "pointer-events", "position", "quotes", "resize", "right", "row-gap",
    "table-layout", "text-align", "text-align-last", "text-decoration",
    "text-decoration-color", "text-decoration-line", "text-decoration-style",
    "text-emphasis", "text-indent", "text-justify", "text-overflow", "text-shadow",
    "text-transform", "text-underline-offset", "top", "transform", "transform-origin",
    "transition", "unicode-bidi", "user-select", "vertical-align", "visibility",
    "white-space", "width", "will-change", "word-break", "word-spacing", "writing-mode",
    "z-index",
})
_MEDIA_FEATURES = frozenset({
    "width", "min-width", "max-width", "height", "min-height", "max-height",
    "aspect-ratio", "min-aspect-ratio", "max-aspect-ratio", "orientation",
    "resolution", "min-resolution", "max-resolution", "color", "min-color",
    "max-color", "color-index", "min-color-index", "max-color-index",
    "monochrome", "color-gamut", "grid", "update", "overflow-block",
    "overflow-inline", "display-mode", "dynamic-range", "hover", "any-hover",
    "pointer", "any-pointer", "prefers-color-scheme", "prefers-contrast",
    "prefers-reduced-motion", "prefers-reduced-data", "forced-colors",
    "inverted-colors", "scripting", "device-width", "min-device-width",
    "max-device-width", "device-height", "min-device-height", "max-device-height",
})
_PREVIEW_VIEWPORT_PX = (1280.0, 800.0)
_CSS_HEX = frozenset("0123456789abcdefABCDEF")
_CSS_ESCAPE_WS = frozenset(" \t\n\r\f")
HTML_TAG_NAME = re.compile(r"^[a-z][a-z0-9-]*$", re.I)


def html_tag_name(tag: str) -> str:
    ltag = (tag or "").lower()
    return "img" if ltag == "image" else ltag


def end_tag_matches(open_tag: str, end_tag: str) -> bool:
    if open_tag == end_tag:
        return True
    return open_tag in HEADING_TAGS and end_tag in HEADING_TAGS


HTML_COMMENT_OPEN = "<!--"
HTML_COMMENT_CLOSE = "-->"
HTML_BLOCK_OPEN = re.compile(
    r"(?i)^ {0,3}</?(?:address|article|aside|base|basefont|blockquote|body|"
    r"caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|"
    r"figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|"
    r"html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|"
    r"optgroup|option|p|param|search|section|source|summary|table|tbody|td|"
    r"tfoot|th|thead|title|tr|track|ul)(?:\s|/?>|$)"
)
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
    "object": "出现禁止标签",
    "embed": "出现禁止标签",
    "pre": "禁止 <pre>/<code>，代码块请逐行 <p>",
    "code": "禁止 <pre>/<code>，代码块请逐行 <p>",
    "meta": "出现禁止标签",
    "base": "出现禁止标签",
    "plaintext": "出现禁止标签",
    "xmp": "出现禁止标签",
    "link": "出现禁止标签",
    "template": "出现禁止标签",
    "html": "出现 <html>/<head>/<body>，组件须为可粘贴片段",
    "head": "出现 <html>/<head>/<body>，组件须为可粘贴片段",
    "body": "出现 <html>/<head>/<body>，组件须为可粘贴片段",
    "title": "出现 <title>，组件须为可粘贴片段",
    "select": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "option": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "optgroup": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "dialog": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
    "details": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
    "noscript": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
}
THEME_NEED_STYLE = {
    "section",
    "p",
    "h1",
    "h2",
    "h3",
    "ul",
    "ol",
    "li",
    "table",
    "tr",
    "td",
    "th",
    "figure",
    "figcaption",
    "img",
    "blockquote",
    "hr",
    "h4",
    "h5",
    "h6",
    "article",
    "address",
    "header",
    "footer",
    "main",
    "nav",
    "dl",
    "dt",
    "dd",
    "aside",
}
LEAF_BLOCK_TAGS = frozenset({
    "address",
    "article",
    "aside",
    "blockquote",
    "caption",
    "details",
    "dialog",
    "div",
    "dl",
    "dt",
    "dd",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "li",
    "main",
    "menu",
    "nav",
    "ol",
    "p",
    "pre",
    "search",
    "section",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
})
IMPLIED_END_ON_START = {
    "li": frozenset({"li"}),
    "dt": frozenset({"dt", "dd"}),
    "dd": frozenset({"dt", "dd"}),
    "td": frozenset({"td", "th"}),
    "th": frozenset({"td", "th"}),
    "tr": frozenset({"tr"}),
    "p": frozenset({"p"}),
}
IMPLIED_END_STOP = frozenset({
    "ul",
    "ol",
    "dl",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "section",
    "figure",
    "blockquote",
    "html",
    "body",
})
LIST_ITEM_SCOPE_STOP = frozenset({
    "ul",
    "ol",
    "html",
    "body",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "td",
    "th",
    "caption",
    "template",
})
P_CLOSING_START = frozenset({
    "address",
    "article",
    "aside",
    "blockquote",
    "details",
    "div",
    "dl",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "main",
    "menu",
    "nav",
    "ol",
    "p",
    "pre",
    "search",
    "section",
    "table",
    "ul",
    "li",
    "dt",
    "dd",
})
TABLE_START = frozenset({
    "tr",
    "td",
    "th",
    "thead",
    "tbody",
    "tfoot",
    "caption",
    "colgroup",
    "col",
})
TABLE_SECTION = frozenset({"thead", "tbody", "tfoot"})
TABLE_CONTEXT = frozenset({
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "caption",
    "colgroup",
    "html",
    "body",
    "template",
})
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


ACTIVE_DATA_TOKEN = re.compile(r"(?:html|svg|xml|javascript|ecmascript)", re.I)
PREVIEW_SKIP_TAGS = {
    "head",
    "title",
    "style",
    "script",
    "noscript",
    "template",
    "meta",
    "link",
    "base",
    "source",
    "track",
    "area",
    "col",
    "param",
    "datalist",
    "select",
    "option",
    "optgroup",
}
PREVIEW_FALLBACK_TAGS = {"iframe", "canvas", "object", "video", "audio"}
STYLE_TAG = re.compile(r"<style\b([^>]*)>(.*?)</style>", re.I | re.S)
CSS_COMBINATOR = re.compile(r"\s*[>+~]\s*|\s+")
PREVIEW_MARKER_ATTRS = {"id", "class", "name"}
PREVIEW_BLOCK_BREAK = {
    "p",
    "section",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "blockquote",
    "figure",
    "figcaption",
    "hr",
    "br",
    "pre",
    "header",
    "footer",
    "article",
    "aside",
    "nav",
    "main",
    "body",
    "html",
    "address",
    "dl",
    "dt",
    "dd",
}
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*$")
HTML_TYPE1_OPEN = re.compile(r"(?i)^ {0,3}<(script|pre|style|textarea)(?:\s|>|$)")
HTML_TYPE1_CLOSE = re.compile(r"(?i)</(script|pre|style|textarea)>")
HTML_UNTIL_OPEN = [
    (re.compile(r"^ {0,3}<!--"), "-->"),
    (re.compile(r"^ {0,3}<\?"), "?>"),
    (re.compile(r"^ {0,3}<!\[CDATA\["), "]]>"),
    (re.compile(r"^ {0,3}<![A-Z]"), ">"),
]
HTML_TYPE7_TAG = re.compile(r"^ {0,3}</?[a-zA-Z][a-zA-Z0-9-]*")
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:\s|$)")
MD_LIST = re.compile(r"^ {0,3}(?:[-*+]|\d+[.)])\s")
MD_QUOTE = re.compile(r"^ {0,3}>")
MD_THEMATIC = re.compile(r"^ {0,3}(?:(?:-[ \t]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?:=+|-+)\s*$")
LINK_REF_DEF = re.compile(r"^ {0,3}\[[^\]\n]+\]:\s+\S")
LINK_REF_DEF_OPEN = re.compile(r"^ {0,3}\[[^\]\n]+\]:\s*$")


def indent_columns(raw: str) -> int:
    """CommonMark indent width: spaces count 1, tabs advance to the next multiple of 4."""
    cols = 0
    for ch in raw:
        if ch == " ":
            cols += 1
        elif ch == "\t":
            cols += 4 - (cols % 4)
        else:
            break
    return cols


def is_indented_code_line(raw: str) -> bool:
    return indent_columns(raw) >= 4


def is_paragraph_line(raw: str, *, in_paragraph: bool = False) -> bool:
    """True when a Markdown line continues or starts a paragraph (not another block)."""
    if not raw.strip():
        return False
    if is_indented_code_line(raw):
        # Indented code cannot interrupt a paragraph (lazy continuation).
        return in_paragraph
    if ATX_HEADING.match(raw) or MD_LIST.match(raw) or MD_QUOTE.match(raw) or MD_THEMATIC.match(raw):
        return False
    if FENCE_OPEN.match(raw):
        return False
    if not in_paragraph and (LINK_REF_DEF.match(raw) or LINK_REF_DEF_OPEN.match(raw)):
        return False
    return True


def is_setext_underline(raw: str) -> bool:
    return bool(SETEXT_UNDERLINE.match(raw))


def data_uri_media_type(value: str) -> str:
    """MIME type of a data: URI: after data:, before the first ';' or ','."""
    text = value.lower()
    if not text.startswith("data:"):
        return ""
    rest = text[5:]
    cut = len(rest)
    for sep in ";,":
        idx = rest.find(sep)
        if idx != -1:
            cut = min(cut, idx)
    return rest[:cut].strip()


def is_executable_url(value: str) -> bool:
    if not value:
        return False
    text = SCHEME_IGNORED.sub("", value)
    if EXEC_SCHEME.search(text):
        return True
    lower = text.lower()
    if lower.startswith("data:"):
        return bool(ACTIVE_DATA_TOKEN.search(data_uri_media_type(lower)))
    return False


def attr_values(attrs, name: str) -> list[str]:
    lname = name.lower()
    return [(value or "") for key, value in attrs if key.lower() == lname]


def _duplicates(items: list[str]) -> list[str]:
    return sorted({item for item in items if items.count(item) > 1})


def normalize_sig_token(token: str) -> str:
    text = token.lower().strip("`")
    if text.startswith("sig:"):
        text = text[4:]
    if not text.startswith("sig-"):
        text = "sig-" + text
    return text


def recipe_positive_body(body: str) -> str:
    """Recipe text with exclusion verb + coordinated slot/sig tokens removed."""
    slot_alt = "|".join(re.escape(s) for s in REQUIRED_SLOTS)
    ident = rf"(?:slot:)?(?:{slot_alt})|sig:[a-z0-9-]+|sig-[a-z0-9-]+"
    token = rf"\s*`?(?:{ident})"
    connector = r"(?:和|与|以及|还有|及|、|,|，)"
    pieces: list[str] = []
    i = 0
    for match in RECIPE_EXCLUDE_VERB.finditer(body):
        pieces.append(body[i : match.start()])
        rest = body[match.end() :]
        found = re.match(token, rest, re.I)
        consumed = found.end() if found else 0
        more = rest[consumed:]
        while found:
            extra = re.match(rf"\s*{connector}{token}", more, re.I)
            if not extra:
                break
            consumed += extra.end()
            more = rest[consumed:]
        i = match.end() + consumed
    pieces.append(body[i:])
    return "".join(pieces)


def recipe_has_declared_sig(body: str, sig_ids: set[str]) -> bool:
    declared = {normalize_sig_token(item) for item in sig_ids}
    return any(normalize_sig_token(match.group(0)) in declared for match in RECIPE_SIG.finditer(body))


def recipe_has_exclude(body: str, *, sig_ids: set[str]) -> bool:
    """True when an exclusion verb is followed by a declared slot or signature id."""
    declared_sigs = {normalize_sig_token(item) for item in sig_ids}
    slot_alt = "|".join(re.escape(s) for s in REQUIRED_SLOTS)
    for match in RECIPE_EXCLUDE_VERB.finditer(body):
        rest = body[match.end() :]
        found = re.match(
            rf"\s*`?((?:slot:)?(?:{slot_alt})|sig:[a-z0-9-]+|sig-[a-z0-9-]+)",
            rest,
            re.I,
        )
        if not found:
            continue
        token = found.group(1)
        low = token.lower()
        if low.startswith("slot:"):
            low = low[5:]
        if low in {s.lower() for s in REQUIRED_SLOTS}:
            return True
        if normalize_sig_token(token) in declared_sigs:
            return True
    return False


def recipe_body_usable(body: str, *, sig_ids: set[str]) -> bool:
    """True when a recipe names core slots, a declared signature id, and an excluded slot."""
    positive = recipe_positive_body(body)
    return bool(
        RECIPE_SLOT.search(positive)
        and recipe_has_declared_sig(positive, sig_ids)
        and recipe_has_exclude(body, sig_ids=sig_ids)
    )


def recipe_entry_ids(section: str, sig_ids: set[str]) -> set[str]:
    found: set[str] = set()
    for raw in section.splitlines():
        if is_indented_code_line(raw):
            continue
        line = raw.strip()
        listed = RECIPE_LIST.match(line)
        if listed:
            if recipe_body_usable(listed.group(2), sig_ids=sig_ids):
                found.add(listed.group(1).lower())
            continue
        if line.startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if cells and re.fullmatch(r"[a-z][a-z0-9_-]*", cells[0], re.I):
                rest = [cell for cell in cells[1:] if cell and not re.fullmatch(r":?-{3,}:?", cell)]
                if rest and recipe_body_usable(" ".join(rest), sig_ids=sig_ids):
                    found.add(cells[0].lower())
            continue
        plain = RECIPE_PLAIN.match(line)
        if plain and recipe_body_usable(plain.group(2), sig_ids=sig_ids):
            found.add(plain.group(1).lower())
    return found


def _markdown_code_span_ranges(text: str) -> list[tuple[int, int]]:
    """Inclusive-start, exclusive-end ranges of CommonMark inline code spans."""
    ranges: list[tuple[int, int]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "`":
            i += 1
            continue
        start = i
        while i < n and text[i] == "`":
            i += 1
        opener_len = i - start
        j = i
        closer = None
        while j < n:
            if text[j] != "`":
                j += 1
                continue
            k = j
            while k < n and text[k] == "`":
                k += 1
            if k - j == opener_len:
                closer = k
                break
            j = k
        if closer is None:
            continue
        ranges.append((start, closer))
        i = closer
    return ranges


def _in_index_ranges(pos: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in ranges)


def strip_html_comments(text: str, *, markdown: bool = False) -> str:
    """Remove HTML comments. An unclosed comment hides through end of text."""
    skip: list[tuple[int, int]] = []
    if markdown:
        for fence in iter_top_level_fences(text):
            skip.append((fence["start"], fence["end"]))
        for start, end in unfenced_spans(text):
            for span_start, span_end in _markdown_code_span_ranges(text[start:end]):
                skip.append((start + span_start, start + span_end))
    pieces: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        start = text.find(HTML_COMMENT_OPEN, i)
        while start != -1 and _in_index_ranges(start, skip):
            start = text.find(HTML_COMMENT_OPEN, start + 1)
        if start == -1:
            pieces.append(text[i:])
            break
        pieces.append(text[i:start])
        end = text.find(HTML_COMMENT_CLOSE, start + len(HTML_COMMENT_OPEN))
        if end == -1:
            break
        i = end + len(HTML_COMMENT_CLOSE)
    return "".join(pieces)


def html_body_has_element(body: str) -> bool:
    """True when a fence parsed into at least one completed start tag."""
    visible = strip_html_comments(body)
    counter = _CompletedTagCounter()
    try:
        counter.feed(visible)
        counter.close()
    except Exception:  # noqa: BLE001
        return False
    return counter.starts > 0


ROOT_WRAPPER_TAGS = frozenset({"section", "article", "header", "footer", "main", "nav", "aside"})


class _FenceUsableCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.has_placeholder = False
        self.stack: list[str] = []
        self.top_level: list[str] = []

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag: str, attrs) -> None:
        ltag = html_tag_name(tag)
        at_root = not self.stack
        if ltag in TABLE_START and "table" not in self.stack:
            return
        if at_root:
            self.top_level.append(ltag)
        self.tags.append(ltag)
        if ltag not in VOID_TAGS:
            self.stack.append(ltag)

    def handle_endtag(self, tag: str) -> None:
        ltag = html_tag_name(tag)
        if ltag not in self.stack:
            return
        while self.stack:
            top = self.stack.pop()
            if top == ltag:
                return

    def handle_data(self, data: str) -> None:
        if not self.stack and (data or "").strip():
            self.top_level.append("#text")
        if any(t in SKIP_TAGS for t in self.stack):
            return
        if PLACEHOLDER.search(data or ""):
            self.has_placeholder = True


def html_fence_usable(body: str, kind: str, ident: str) -> bool:
    """True when a component fence has a placeholder or slot-specific usable content."""
    visible = strip_html_comments(body)
    collector = _FenceUsableCollector()
    try:
        collector.feed(visible)
        collector.close()
    except Exception:  # noqa: BLE001
        pass
    if ident == "root":
        return collector.top_level == ["section"]
    if collector.has_placeholder:
        return True
    if kind == "sig":
        return False
    tags = collector.tags
    if ident == "divider":
        return any(tag in {"hr", "br"} for tag in tags)
    if ident in {"image", "image_gif"}:
        return "img" in tags
    return False


class _CompletedTagCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.starts = 0
        self.stack: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        ltag = html_tag_name(tag)
        if ltag in TABLE_START and "table" not in self.stack:
            return
        self.starts += 1
        if ltag not in VOID_TAGS:
            self.stack.append(ltag)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        ltag = html_tag_name(tag)
        if ltag not in self.stack:
            return
        while self.stack:
            top = self.stack.pop()
            if top == ltag:
                return


def strip_css_comments(text: str) -> str:
    """Remove /* */ comments, leaving delimiters that appear inside quoted strings."""
    out: list[str] = []
    i = 0
    n = len(text or "")
    quote = None
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            j = text.find("*/", i + 2)
            if j == -1:
                break
            i = j + 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def decode_css_escapes(text: str) -> str:
    """Decode CSS identifier escapes such as pos\\69 tion → position."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch != "\\" or i + 1 >= n:
            out.append(ch)
            i += 1
            continue
        nxt = text[i + 1]
        if nxt in "\n\f" or nxt == "\r":
            i += 2
            if nxt == "\r" and i < n and text[i] == "\n":
                i += 1
            continue
        if nxt in _CSS_HEX:
            j = i + 1
            hex_chars: list[str] = []
            while j < n and len(hex_chars) < 6 and text[j] in _CSS_HEX:
                hex_chars.append(text[j])
                j += 1
            if j < n and text[j] in _CSS_ESCAPE_WS:
                if text[j] == "\r" and j + 1 < n and text[j + 1] == "\n":
                    j += 2
                else:
                    j += 1
            code = int("".join(hex_chars), 16)
            if 0 < code <= 0x10FFFF:
                out.append(chr(code))
            else:
                out.append("\ufffd")
            i = j
            continue
        out.append(nxt)
        i += 2
    return "".join(out)


def normalize_style(style: str) -> str:
    """Strip CSS comments then decode identifier escapes."""
    return decode_css_escapes(strip_css_comments(style or ""))


def css_numeric_opacity(token: str) -> float | None:
    """Parse a number, percentage, or simple calc() wrapping either."""
    text = (token or "").strip().lower()
    if text.startswith("calc(") and text.endswith(")"):
        return css_numeric_opacity(text[5:-1])
    if text.endswith("%"):
        try:
            return float(text[:-1]) / 100.0
        except ValueError:
            return None
    try:
        return float(text)
    except ValueError:
        return None


def css_decl_value_applies(prop: str, token: str) -> bool:
    """False when a declaration value is ignored by CSS (invalid token)."""
    if not token:
        return False
    if prop == "display":
        return token in _CSS_DISPLAY_OK or token.startswith("-")
    if prop == "visibility":
        return token in _CSS_VIS_OK
    if prop == "opacity":
        if css_numeric_opacity(token) is not None:
            return True
        low = token.lower()
        return low.startswith("calc(") and low.endswith(")")
    return True


def css_property_applies(prop: str) -> bool:
    if prop.startswith("--"):
        return True
    if prop.startswith("-") and prop.count("-") >= 2:
        return True
    return prop in CSS_KNOWN_PROPS


def css_decl_is_applied(prop: str, value: str) -> bool:
    token = CSS_IMPORTANT.sub("", value).strip().split()[0] if value.strip() else ""
    return css_property_applies(prop) and css_decl_value_applies(prop, token)


def is_html_type7_line(raw: str) -> bool:
    """True when the line is a complete HTML start or end tag (CommonMark type 7)."""
    match = HTML_TYPE7_TAG.match(raw)
    if not match:
        return False
    is_end = bool(re.match(r"^ {0,3}</", match.group(0)))
    i = match.end()
    n = len(raw)
    if is_end:
        while i < n and raw[i] in " \t":
            i += 1
        return i < n and raw[i] == ">" and raw[i + 1 :].strip() == ""
    while i < n:
        while i < n and raw[i] in " \t":
            i += 1
        if i >= n:
            return False
        if raw[i] == ">":
            return raw[i + 1 :].strip() == ""
        if raw[i] == "/":
            i += 1
            while i < n and raw[i] in " \t":
                i += 1
            return i < n and raw[i] == ">" and raw[i + 1 :].strip() == ""
        if raw[i] in "\"'=<":
            return False
        name_start = i
        while i < n and raw[i] not in " \t\"'=/<>":
            i += 1
        if i == name_start or not HTML_ATTR_NAME.fullmatch(raw[name_start:i]):
            return False
        if i >= n:
            return False
        while i < n and raw[i] in " \t":
            i += 1
        if i < n and raw[i] == "=":
            i += 1
            while i < n and raw[i] in " \t":
                i += 1
            if i >= n:
                return False
            if raw[i] in "\"'":
                quote = raw[i]
                i += 1
                while i < n and raw[i] != quote:
                    i += 1
                if i >= n:
                    return False
                i += 1
            else:
                if raw[i] in "\"'=<`>":
                    return False
                started = False
                while i < n and raw[i] not in " \t\"'=<`>":
                    started = True
                    i += 1
                if not started:
                    return False
    return False


def iter_css_declarations(style: str):
    stripped = normalize_style(style)
    for part in stripped.split(";"):
        piece = part.strip()
        if ":" not in piece:
            continue
        prop, value = piece.split(":", 1)
        prop, value = prop.strip().lower(), value.strip()
        if prop and value:
            yield prop, value


def has_css_declaration(style: str) -> bool:
    for prop, value in iter_css_declarations(style):
        if css_decl_is_applied(prop, value):
            return True
    return False


def _cascade_put(winning: dict, key: str, value, important: bool) -> None:
    prev = winning.get(key)
    if prev is not None and prev[1] and not important:
        return
    winning[key] = (value, important)


def _apply_all_reset(
    winning: dict,
    important: bool,
    keyword: str = "initial",
    extras: dict | None = None,
) -> None:
    kw = (keyword or "initial").split()[0].lower()
    extras = extras or {}
    keys = set(winning) | set(extras)
    for key in keys:
        if key in {"unicode-bidi", "direction"}:
            continue
        if key in extras:
            initial = extras[key]
            if kw == "inherit":
                val = "inherit"
            elif kw == "unset":
                val = "inherit" if key == "visibility" else initial
            elif kw in {"initial", "revert", "revert-layer"}:
                val = initial
            else:
                val = kw
        else:
            val = kw
        _cascade_put(winning, key, val, important)


_DECL_ALL_INITIAL = {
    "display": "inline",
    "opacity": "1",
    "visibility": "visible",
}
_LAYOUT_ALL_INITIAL = {
    "max-width": "none",
    "height": "auto",
    "display": "inline",
    "font-size": "medium",
    "visibility": "visible",
}
_MARGIN_ALL_INITIAL = {
    "top": "0",
    "right": "0",
    "bottom": "0",
    "left": "0",
}


_FONT_PREFIX = frozenset({
    "normal", "italic", "oblique", "bold", "bolder", "lighter", "small-caps",
    "ultra-condensed", "extra-condensed", "condensed", "semi-condensed",
    "semi-expanded", "expanded", "extra-expanded", "ultra-expanded",
})
_FONT_SYSTEM = frozenset({
    "caption", "icon", "menu", "message-box", "small-caption", "status-bar",
})


def css_font_size_value_ok(raw: str) -> bool:
    """True when a font-size declaration is a single valid size token (or calc())."""
    text = (raw or "").strip().lower()
    if not text:
        return False
    if text.startswith("calc("):
        return text.endswith(")")
    parts = text.split()
    if len(parts) != 1:
        return False
    token = parts[0]
    if token in {
        "xx-small", "x-small", "small", "medium", "large", "x-large", "xx-large",
        "xxx-large", "larger", "smaller", "math",
    }:
        return True
    return bool(re.fullmatch(
        r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?(?:[a-z%]+)?",
        token,
    ))


def font_shorthand_size(value: str) -> str | None:
    text = (value or "").strip()
    if not text:
        return None
    low = text.lower()
    if low in _FONT_SYSTEM:
        return low
    for tok in text.split():
        piece = tok.split("/", 1)[0]
        pl = piece.lower()
        if pl in _FONT_PREFIX or re.fullmatch(r"[1-9]00", pl):
            continue
        return piece
    return None


def winning_style_decls(style: str) -> dict[str, tuple[str, bool]]:
    """Winning CSS declarations: prop -> (token, important)."""
    winning: dict[str, tuple[str, bool]] = {}
    for prop, value in iter_css_declarations(style):
        important = bool(CSS_IMPORTANT.search(value))
        raw = CSS_IMPORTANT.sub("", value).strip()
        token = raw.split()[0].lower() if raw else ""
        if prop == "all":
            _apply_all_reset(winning, important, token or "initial", extras=_DECL_ALL_INITIAL)
            continue
        if not css_decl_value_applies(prop, token):
            continue
        _cascade_put(winning, prop, token, important)
    return winning


def winning_style_raw(style: str) -> dict[str, str]:
    """Winning CSS declarations: prop -> full value (without !important)."""
    winning: dict[str, tuple[str, bool]] = {}
    for prop, value in iter_css_declarations(style):
        important = bool(CSS_IMPORTANT.search(value))
        raw = CSS_IMPORTANT.sub("", value).strip().lower()
        token = raw.split()[0] if raw else ""
        if prop == "all":
            _apply_all_reset(winning, important, token or "initial", extras=_LAYOUT_ALL_INITIAL)
            continue
        if prop == "font":
            size = font_shorthand_size(raw)
            if size:
                _cascade_put(winning, "font-size", size, important)
            continue
        if prop == "font-size" and not css_font_size_value_ok(raw):
            continue
        if prop in {"display", "opacity", "visibility"} and not css_decl_value_applies(prop, token):
            continue
        _cascade_put(winning, prop, raw, important)
    return {prop: raw for prop, (raw, _imp) in winning.items()}


def _expand_box_sides(parts: list[str]) -> tuple[str, str, str, str] | None:
    if len(parts) == 1:
        return parts[0], parts[0], parts[0], parts[0]
    if len(parts) == 2:
        return parts[0], parts[1], parts[0], parts[1]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2], parts[1]
    if len(parts) >= 4:
        return parts[0], parts[1], parts[2], parts[3]
    return None


def winning_margin_sides(style: str) -> dict[str, str]:
    """Winning margin-top/right/bottom/left after shorthand vs longhand cascade."""
    winning: dict[str, tuple[str, bool]] = {}
    for prop, value in iter_css_declarations(style):
        important = bool(CSS_IMPORTANT.search(value))
        raw = CSS_IMPORTANT.sub("", value).strip().lower()
        if prop == "all":
            _apply_all_reset(winning, important, raw.split()[0] if raw else "initial", extras=_MARGIN_ALL_INITIAL)
            continue
        if prop == "margin":
            expanded = _expand_box_sides(raw.split())
            if not expanded:
                continue
            for side, val in zip(("top", "right", "bottom", "left"), expanded):
                _cascade_put(winning, side, val, important)
        elif prop in {"margin-top", "margin-right", "margin-bottom", "margin-left"}:
            side = prop.split("-", 1)[1]
            _cascade_put(winning, side, raw, important)
    return {side: val for side, (val, _imp) in winning.items()}


def _margin_horizontal_auto(style: str) -> bool:
    sides = winning_margin_sides(style)
    return sides.get("left") == "auto" and sides.get("right") == "auto"


def has_root_layout(style: str) -> bool:
    vals = winning_style_raw(style)
    mw = re.sub(r"\s+", "", vals.get("max-width", ""))
    return mw == "677px" and _margin_horizontal_auto(style)


def has_responsive_image_style(style: str) -> bool:
    vals = winning_style_raw(style)
    mw = re.sub(r"\s+", "", vals.get("max-width", ""))
    height = re.sub(r"\s+", "", vals.get("height", ""))
    display = (vals.get("display", "").split() or [""])[0]
    return mw == "100%" and height == "auto" and display == "block" and _margin_horizontal_auto(style)


_CSS_ABS_PX = {
    "px": 1.0,
    "pt": 96.0 / 72.0,
    "pc": 16.0,
    "in": 96.0,
    "cm": 96.0 / 2.54,
    "mm": 96.0 / 25.4,
    "q": 96.0 / 101.6,
}


def css_length_px(value: str) -> float | None:
    text = (value or "").strip().lower()
    match = re.match(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)([a-z%]*)$", text)
    if not match:
        return None
    num = float(match.group(1))
    unit = match.group(2) or "px"
    if unit in _CSS_ABS_PX:
        return num * _CSS_ABS_PX[unit]
    return None


def font_size_limit_hits(style: str) -> list[str]:
    raw = winning_style_raw(style).get("font-size", "")
    if not raw:
        return []
    token = raw.split()[0]
    px = css_length_px(token)
    if px is None or px > 24:
        return [token]
    return []


def winning_style_tokens(style: str) -> dict[str, str]:
    return {prop: token for prop, (token, _imp) in winning_style_decls(style).items()}


def _opacity_is_zero(token: str) -> bool:
    if not token:
        return False
    num = css_numeric_opacity(token)
    if num is not None:
        return num == 0
    low = token.strip().lower()
    return low.startswith("calc(") and low.endswith(")")


def inline_style_hard_hides(style: str) -> bool:
    tokens = winning_style_tokens(style)
    if tokens.get("display") == "none":
        return True
    return _opacity_is_zero(tokens.get("opacity", ""))


def inline_style_visibility(style: str) -> str | None:
    vis = winning_style_tokens(style).get("visibility")
    if vis in {"hidden", "visible", "collapse"}:
        return vis
    return None


def inline_style_hides(style: str) -> bool:
    if inline_style_hard_hides(style):
        return True
    return inline_style_visibility(style) in {"hidden", "collapse"}


def is_real_html_tag(tag: str) -> bool:
    """True for HTML tag names; false for Markdown autolinks like <https://...>."""
    return bool(HTML_TAG_NAME.match(tag or ""))


class VisibleMarkdownCollector(HTMLParser):
    """Keep markdown that HTML actually renders; drop comments and tagged subtrees."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.parts: list[str] = []

    def handle_startendtag(self, tag: str, attrs) -> None:
        return

    def handle_starttag(self, tag: str, attrs) -> None:
        if is_real_html_tag(tag) and tag.lower() not in VOID_TAGS:
            self.stack.append(tag.lower())

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        if not is_real_html_tag(ltag):
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == ltag:
                del self.stack[i:]
                return

    def handle_data(self, data: str) -> None:
        if not self.stack:
            self.parts.append(data)

    def handle_comment(self, _data: str) -> None:
        return


class HtmlBlockScanner:
    """CommonMark HTML-block state: type-6/7 last until a blank line, not a matching end tag."""

    def __init__(self) -> None:
        self.type1: str | None = None
        self.until_close: str | None = None
        self.html_block = False
        self.in_paragraph = False
        self.awaiting_link_dest = False

    def _type1_closed(self, raw: str, tag: str) -> bool:
        return bool(re.search(rf"(?i)</{re.escape(tag)}>", raw))

    def _mark_markdown_line(self, raw: str) -> None:
        if not raw.strip():
            self.in_paragraph = False
        elif self.in_paragraph and is_setext_underline(raw):
            self.in_paragraph = False
        elif not self.in_paragraph and LINK_REF_DEF_OPEN.match(raw):
            self.in_paragraph = False
            self.awaiting_link_dest = True
        elif is_paragraph_line(raw, in_paragraph=self.in_paragraph):
            self.in_paragraph = True
        else:
            self.in_paragraph = False

    def in_block(self, raw: str) -> bool:
        if self.awaiting_link_dest:
            cont = indent_columns(raw) >= 1 and bool(raw.strip()) and not is_indented_code_line(raw)
            self.awaiting_link_dest = False
            if cont:
                self.in_paragraph = False
                return False
        if self.type1:
            if self._type1_closed(raw, self.type1):
                self.type1 = None
            self.in_paragraph = False
            return True
        if self.until_close is not None:
            if self.until_close in raw:
                self.until_close = None
            self.in_paragraph = False
            return True
        if self.html_block:
            if not raw.strip():
                self.html_block = False
                self.in_paragraph = False
            else:
                self.in_paragraph = False
            return True
        type1_open = HTML_TYPE1_OPEN.match(raw)
        if type1_open:
            self.type1 = type1_open.group(1).lower()
            if self._type1_closed(raw, self.type1):
                self.type1 = None
            self.in_paragraph = False
            return True
        for rx, closer in HTML_UNTIL_OPEN:
            if rx.match(raw):
                if closer not in raw:
                    self.until_close = closer
                self.in_paragraph = False
                return True
        if HTML_BLOCK_OPEN.match(raw):
            self.html_block = True
            self.in_paragraph = False
            return True
        if is_html_type7_line(raw) and not self.in_paragraph:
            self.html_block = True
            self.in_paragraph = False
            return True
        self._mark_markdown_line(raw)
        return False


def strip_html_blocks(text: str) -> str:
    """Drop CommonMark HTML block lines; keep markdown that follows a blank line."""
    scanner = HtmlBlockScanner()
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        if scanner.in_block(raw):
            out.append("\n" if line.endswith(("\n", "\r")) else "")
        else:
            out.append(line)
    return "".join(out)


def visible_structure_markdown(text: str) -> str:
    """Markdown that survives fences, HTML comments, and raw HTML blocks."""
    return strip_html_comments(strip_html_blocks(unfenced_markdown(text)), markdown=True)


def has_preview_marker(haystack: str, ident: str, *prefixes: str) -> bool:
    for prefix in prefixes:
        needle = f"{prefix}{ident}"
        start = 0
        while True:
            idx = haystack.find(needle, start)
            if idx == -1:
                break
            end = idx + len(needle)
            left_ok = idx == 0 or not PREVIEW_ID_TAIL.match(haystack[idx - 1])
            right_ok = end == len(haystack) or not PREVIEW_ID_TAIL.match(haystack[end])
            if left_ok and right_ok:
                return True
            start = idx + 1
    return False


def split_selector_list(text: str) -> list[str]:
    """Split a selector list on commas that are outside quotes, [], and ()."""
    parts: list[str] = []
    depth_brack = 0
    depth_paren = 0
    quote = None
    start = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "[":
            depth_brack += 1
        elif ch == "]" and depth_brack:
            depth_brack -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")" and depth_paren:
            depth_paren -= 1
        elif ch == "," and depth_brack == 0 and depth_paren == 0:
            piece = text[start:i].strip()
            if piece:
                parts.append(piece)
            start = i + 1
        i += 1
    piece = text[start:].strip()
    if piece:
        parts.append(piece)
    return parts


class _StartTagAttrParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.attrs: dict[str, str] = {}

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag: str, attrs) -> None:
        if not self.attrs:
            self.attrs = {key.lower(): (value or "") for key, value in attrs}


def html_start_attrs(attr_text: str) -> dict[str, str]:
    parser = _StartTagAttrParser()
    try:
        parser.feed(f"<style {attr_text}>")
        parser.close()
    except Exception:  # noqa: BLE001
        return {}
    return parser.attrs


_MEDIA_TYPES = frozenset({
    "all",
    "screen",
    "print",
    "speech",
    "tty",
    "tv",
    "projection",
    "handheld",
    "braille",
    "embossed",
    "aural",
})


def _split_media_list(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")" and depth:
            depth -= 1
        elif ch == "," and depth == 0:
            piece = text[start:i].strip()
            if piece:
                parts.append(piece)
            start = i + 1
    piece = text[start:].strip()
    if piece:
        parts.append(piece)
    return parts


def media_applies_to_screen(media: str | None) -> bool:
    """True when a <style media> list applies to a screen preview."""
    if media is None:
        return True
    text = media.strip()
    if not text:
        return True
    return any(_media_query_applies(query) for query in _split_media_list(text) if query.strip())


def _media_query_applies(query: str) -> bool:
    q = query.strip().lower()
    if not q:
        return False
    negate = False
    if q.startswith("only "):
        q = q[5:].lstrip()
    elif q.startswith("not "):
        negate = True
        q = q[4:].lstrip()
    match = re.match(r"^([a-z]+)\b(.*)$", q)
    if match and match.group(1) in _MEDIA_TYPES:
        mtype = match.group(1)
        rest = match.group(2).strip()
        matches = mtype in {"all", "screen"} and _media_features_apply(rest)
    else:
        matches = _media_features_apply(q)
    return (not matches) if negate else matches


def _media_features_apply(text: str) -> bool:
    q = text.strip()
    if not q:
        return True
    if q.lower().startswith("and") and (len(q) == 3 or not q[3].isalnum()):
        q = q[3:].strip()
        if not q:
            return False
    or_parts = _split_supports_keyword(q, "or")
    if len(or_parts) > 1:
        return any(_media_features_apply(part) for part in or_parts)
    and_parts = _split_supports_keyword(q, "and")
    if len(and_parts) > 1:
        return all(_media_features_apply(part) for part in and_parts)
    lower = q.lower()
    if lower.startswith("not") and (len(q) == 3 or not q[3].isalnum()):
        return not _media_features_apply(q[3:].strip())
    inner = _unwrap_supports_parens(q)
    if inner != q:
        return _media_features_apply(inner)
    match = re.match(r"^([a-z-]+)\s*(?::\s*(.+))?$", inner.strip(), re.I)
    if not match:
        return False
    return _media_feature_applies(match.group(1).lower(), (match.group(2) or "").strip())


def _media_feature_applies(name: str, value: str) -> bool:
    if name not in _MEDIA_FEATURES:
        return False
    vw, vh = _PREVIEW_VIEWPORT_PX
    token = value.split()[0].lower() if value else ""
    if name in {"width", "min-width", "max-width", "device-width", "min-device-width", "max-device-width"}:
        if not token:
            return name in {"width", "device-width"}
        px = css_length_px(token)
        if px is None:
            return False
        if name.startswith("min"):
            return vw >= px
        if name.startswith("max"):
            return vw <= px
        return abs(vw - px) < 0.5
    if name in {"height", "min-height", "max-height", "device-height", "min-device-height", "max-device-height"}:
        if not token:
            return name in {"height", "device-height"}
        px = css_length_px(token)
        if px is None:
            return False
        if name.startswith("min"):
            return vh >= px
        if name.startswith("max"):
            return vh <= px
        return abs(vh - px) < 0.5
    if name == "orientation":
        return token in {"", "landscape"}
    if name in {"hover", "any-hover"}:
        return token in {"", "hover"}
    if name in {"pointer", "any-pointer"}:
        return token in {"", "fine"}
    if name == "prefers-color-scheme":
        return token in {"", "light"}
    if name == "prefers-reduced-motion":
        return token in {"", "no-preference"}
    if name == "prefers-contrast":
        return token in {"", "no-preference"}
    if name == "forced-colors":
        return token in {"", "none"}
    if name == "grid":
        return token in {"", "0"}
    if name in {"color", "min-color", "max-color"}:
        actual = 8
        if not token:
            return name == "color"
        if not token.isdigit():
            return False
        bits = int(token)
        if name.startswith("min"):
            return actual >= bits
        if name.startswith("max"):
            return actual <= bits
        return bits <= actual
    if name == "update":
        return token in {"", "fast"}
    if name == "scripting":
        return token in {"", "enabled"}
    if name == "display-mode":
        return token in {"", "browser"}
    return not token


def _split_supports_keyword(text: str, keyword: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    quote = None
    i = 0
    n = len(text)
    last = 0
    kwlen = len(keyword)
    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            i += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and text[i : i + kwlen].lower() == keyword:
            before = text[i - 1] if i else " "
            after = text[i + kwlen] if i + kwlen < n else " "
            if not (before.isalnum() or before == "-") and not (after.isalnum() or after == "-"):
                parts.append(text[last:i].strip())
                i += kwlen
                last = i
                continue
        i += 1
    rest = text[last:].strip()
    if parts:
        if rest:
            parts.append(rest)
        return [item for item in parts if item]
    return [text.strip()] if text.strip() else []


def _unwrap_supports_parens(text: str) -> str:
    current = text.strip()
    while current.startswith("(") and current.endswith(")"):
        depth = 0
        split = False
        for i, ch in enumerate(current):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0 and i != len(current) - 1:
                    split = True
                    break
        if split or depth != 0:
            break
        current = current[1:-1].strip()
    return current


def supports_applies(query: str) -> bool:
    """True for @supports queries a typical screen browser satisfies."""
    text = _unwrap_supports_parens(query or "")
    if not text:
        return True
    or_parts = _split_supports_keyword(text, "or")
    if len(or_parts) > 1:
        return any(supports_applies(part) for part in or_parts)
    and_parts = _split_supports_keyword(text, "and")
    if len(and_parts) > 1:
        return all(supports_applies(part) for part in and_parts)
    lower = text.lower()
    if lower.startswith("not") and (len(text) == 3 or not text[3].isalnum()):
        return not supports_applies(text[3:].strip())
    inner = _unwrap_supports_parens(text)
    if inner != text:
        return supports_applies(inner)
    match = re.match(r"^([A-Za-z-]+)\s*:\s*(.+)$", inner)
    if not match:
        return False
    prop = match.group(1).lower()
    raw = match.group(2).strip()
    token = raw.split()[0].lower() if raw else ""
    return css_property_applies(prop) and css_decl_value_applies(prop, token)


STYLE_SKIP_SUBTREES = frozenset({"template", "script", "noscript"})
FORM_CTRL_TAGS = frozenset({
    "button",
    "input",
    "select",
    "textarea",
    "fieldset",
    "optgroup",
    "option",
})


class _StyleBlockCollector(HTMLParser):
    """Collect <style> text from active document nodes, skipping comments and inert trees."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.in_style = False
        self.cur_attrs: dict[str, str] = {}
        self.buf: list[str] = []
        self.blocks: list[tuple[dict[str, str], str]] = []

    def handle_startendtag(self, tag: str, attrs) -> None:
        if self.skip or self.in_style:
            return
        if tag.lower() in STYLE_SKIP_SUBTREES:
            return

    def handle_starttag(self, tag: str, attrs) -> None:
        ltag = tag.lower()
        if self.skip:
            if ltag in STYLE_SKIP_SUBTREES:
                self.skip += 1
            return
        if ltag in STYLE_SKIP_SUBTREES:
            self.skip = 1
            return
        if ltag == "style":
            self.in_style = True
            self.cur_attrs = {key.lower(): (value or "") for key, value in attrs}
            self.buf = []

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        if self.in_style and ltag == "style":
            self.blocks.append((self.cur_attrs, "".join(self.buf)))
            self.in_style = False
            self.buf = []
            return
        if self.skip and ltag in STYLE_SKIP_SUBTREES:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data: str) -> None:
        if self.in_style and not self.skip:
            self.buf.append(data)


def collect_active_style_blocks(html: str) -> list[tuple[dict[str, str], str]]:
    collector = _StyleBlockCollector()
    try:
        collector.feed(html or "")
        collector.close()
    except Exception:  # noqa: BLE001
        return collector.blocks
    return collector.blocks


def style_block_is_css(attrs: dict[str, str] | None) -> bool:
    """True when a <style> element is treated as a CSS stylesheet."""
    raw = (attrs or {}).get("type", "")
    mime = raw.split(";", 1)[0].strip().lower()
    return mime in {"", "text/css"}


def _css_consume_block(text: str, i: int) -> tuple[str, int]:
    """text[i] is '{'. Return (inner, index after the matching '}')."""
    n = len(text)
    i += 1
    start = i
    depth = 1
    quote = None
    while i < n and depth:
        ch = text[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    return text[start:i], n


def _new_layer_state() -> dict:
    return {"next": 0, "names": {}}


def _register_layer_names(rest: str, state: dict) -> None:
    for part in rest.split(","):
        name = part.strip().lower()
        if not name or name in state["names"]:
            continue
        state["names"][name] = state["next"]
        state["next"] += 1


def _layer_index_for(rest: str, state: dict) -> int:
    text = (rest or "").strip()
    if not text:
        idx = state["next"]
        state["next"] += 1
        return idx
    first = text.split(",", 1)[0].strip().lower()
    _register_layer_names(text, state)
    if first in state["names"]:
        return state["names"][first]
    idx = state["next"]
    state["next"] += 1
    return idx


def iter_css_style_rules(
    css: str,
    *,
    active: bool = True,
    layer_index: int | None = None,
    layer_state: dict | None = None,
):
    """Yield (selector, body, layer_index) for style rules in currently active media."""
    text = strip_css_comments(css or "")
    state = layer_state if layer_state is not None else _new_layer_state()
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        quote = None
        found = False
        while i < n:
            ch = text[i]
            if quote:
                if ch == "\\" and i + 1 < n:
                    i += 2
                    continue
                if ch == quote:
                    quote = None
                i += 1
                continue
            if ch in "\"'":
                quote = ch
                i += 1
                continue
            if ch == "{":
                prelude = text[start:i].strip()
                body, i = _css_consume_block(text, i)
                found = True
                if prelude.startswith("@"):
                    match = re.match(r"@([A-Za-z-]+)", prelude)
                    name = match.group(1).lower() if match else ""
                    if name == "media":
                        query = prelude[match.end() :].strip() if match else ""
                        inner_active = active and media_applies_to_screen(query)
                        yield from iter_css_style_rules(
                            body, active=inner_active, layer_index=layer_index, layer_state=state
                        )
                    elif name == "layer":
                        idx = _layer_index_for(prelude[match.end() :], state)
                        yield from iter_css_style_rules(
                            body, active=active, layer_index=idx, layer_state=state
                        )
                    elif name == "supports":
                        query = prelude[match.end() :].strip() if match else ""
                        yield from iter_css_style_rules(
                            body,
                            active=active and supports_applies(query),
                            layer_index=layer_index,
                            layer_state=state,
                        )
                    elif name in {"scope", "container"}:
                        yield from iter_css_style_rules(
                            body, active=False, layer_index=layer_index, layer_state=state
                        )
                elif active and prelude:
                    yield prelude, body, layer_index
                break
            if ch == ";":
                found = True
                stmt = text[start:i].strip()
                at = re.match(r"@([A-Za-z-]+)", stmt)
                if at and at.group(1).lower() == "layer":
                    _register_layer_names(stmt[at.end() :], state)
                i += 1
                break
            i += 1
        if not found:
            break


def _cascade_layer_beats(important: bool, layer: int | None, other: int | None) -> bool | None:
    """True if `layer` outranks `other` for this importance; None when equal."""
    if layer == other:
        return None
    if important:
        if layer is None:
            return False
        if other is None:
            return True
        return layer < other
    if layer is None:
        return True
    if other is None:
        return False
    return layer > other


def extract_stylesheet_hide_rules(html: str) -> list[tuple[str, dict[str, tuple[str, bool]], int | None]]:
    """Selectors from screen-applied <style> with display/opacity/visibility declarations."""
    rules: list[tuple[str, dict[str, tuple[str, bool]], int | None]] = []
    layer_state = _new_layer_state()
    for attrs, block in collect_active_style_blocks(html):
        if not style_block_is_css(attrs):
            continue
        screen = media_applies_to_screen(attrs.get("media") if "media" in attrs else None)
        for selector_text, body, layer_index in iter_css_style_rules(
            block, active=screen, layer_state=layer_state
        ):
            decls = winning_style_decls(body)
            tracked: dict[str, tuple[str, bool]] = {}
            for prop in ("display", "opacity", "visibility"):
                if prop in decls:
                    tracked[prop] = decls[prop]
            if not tracked:
                continue
            selectors = split_selector_list(selector_text)
            if not selectors or any(not selector_is_valid(item) for item in selectors):
                continue
            for selector in selectors:
                rules.append((selector, tracked, layer_index))
    return rules


def split_selector_chain(selector: str) -> list[tuple[str, str]]:
    """[(combinator, compound), ...] from left to right. First combinator is ''."""
    depth_brack = 0
    depth_paren = 0
    quote = None
    parts: list[tuple[str, str]] = []
    comb = ""
    start = 0
    i = 0
    n = len(selector)
    while i < n:
        ch = selector[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            i += 1
            continue
        if ch == "[":
            depth_brack += 1
        elif ch == "]" and depth_brack:
            depth_brack -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")" and depth_paren:
            depth_paren -= 1
        elif depth_brack == 0 and depth_paren == 0:
            if ch in ">+~":
                compound = selector[start:i].strip()
                if compound:
                    parts.append((comb, compound))
                nxt = ch
                i += 1
                while i < n and selector[i] in " \t":
                    i += 1
                comb = nxt
                start = i
                continue
            if ch in " \t":
                j = i
                while j < n and selector[j] in " \t":
                    j += 1
                if j < n and selector[j] not in ">+~":
                    compound = selector[start:i].strip()
                    if compound:
                        parts.append((comb, compound))
                    comb = " "
                    start = j
                i = j
                continue
        i += 1
    compound = selector[start:].strip()
    if compound:
        parts.append((comb, compound))
    return parts


def css_subject(selector: str) -> str:
    """Rightmost compound selector; do not split inside [], quotes, or ()."""
    chain = split_selector_chain(selector)
    return chain[-1][1] if chain else ""


def strip_css_pseudos(subject: str) -> str:
    depth_brack = 0
    quote = None
    for i, ch in enumerate(subject):
        if quote:
            if ch == quote:
                quote = None
            elif ch == "\\" :
                continue
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "[":
            depth_brack += 1
        elif ch == "]" and depth_brack:
            depth_brack -= 1
        elif ch == ":" and depth_brack == 0:
            return subject[:i]
    return subject


def _subject_specificity(subject: str) -> tuple[int, int, int]:
    ids = 0
    classes = 0
    types = 0
    i = 0
    n = len(subject)
    named = re.match(r"^[a-zA-Z][a-zA-Z0-9-]*", subject)
    if named:
        types += 1
        i = named.end()
    elif n and subject[0] == "*":
        i = 1
    while i < n:
        ch = subject[i]
        if ch == "#":
            ids += 1
            i += 1
            while i < n and subject[i] not in ".#[":
                i += 1
        elif ch == ".":
            classes += 1
            i += 1
            while i < n and subject[i] not in ".#[":
                i += 1
        elif ch == "[":
            classes += 1
            j = i + 1
            quote = None
            while j < n:
                cj = subject[j]
                if quote:
                    if cj == quote:
                        quote = None
                    j += 1
                    continue
                if cj in "\"'":
                    quote = cj
                elif cj == "]":
                    break
                j += 1
            i = j + 1 if j < n else n
        else:
            i += 1
    return ids, classes, types


def css_specificity(selector: str) -> tuple[int, int, int]:
    ids = 0
    classes = 0
    types = 0
    for _comb, compound in split_selector_chain(selector):
        a, b, c = _subject_specificity(strip_css_pseudos(compound))
        ids += a
        classes += b
        types += c
        for name, arg, is_element, malformed in iter_compound_pseudos(compound):
            if malformed:
                continue
            if is_element:
                types += 1
                continue
            if name == "where":
                continue
            if name in {"not", "is"}:
                best = (0, 0, 0)
                for sel in split_selector_list(arg or ""):
                    spec = css_specificity(sel)
                    if spec > best:
                        best = spec
                ids += best[0]
                classes += best[1]
                types += best[2]
                continue
            classes += 1
    return ids, classes, types


def css_attr_selector_matches(inner: str, ad: dict[str, str]) -> bool:
    """Match [attr], [attr=val], and ^= $= *= ~= |= operators, with optional i/s flags."""
    spec = inner.strip()
    case_insensitive = False
    flag_m = re.search(r"\s+([iIsS])\s*$", spec)
    if flag_m:
        case_insensitive = flag_m.group(1).lower() == "i"
        spec = spec[: flag_m.start()].rstrip()
    match = re.match(r"^([A-Za-z_:][\w:.-]*)\s*(?:(~=|\|=|\^=|\$=|\*=|=)\s*(.*))?$", spec)
    if not match:
        return False
    name = match.group(1).lower()
    op = match.group(2)
    if op is None:
        return name in ad
    raw_val = (match.group(3) or "").strip()
    if len(raw_val) >= 2 and raw_val[0] == raw_val[-1] and raw_val[0] in "\"'":
        val = raw_val[1:-1]
    else:
        val = raw_val
    actual = ad.get(name)
    if actual is None:
        return False

    def fold(text: str) -> str:
        return text.lower() if case_insensitive else text

    actual_c = fold(actual)
    val_c = fold(val)
    if op == "=":
        return actual_c == val_c
    if not val:
        return False
    if op == "^=":
        return actual_c.startswith(val_c)
    if op == "$=":
        return actual_c.endswith(val_c)
    if op == "*=":
        return val_c in actual_c
    if op == "~=":
        return val_c in actual_c.split()
    if op == "|=":
        return actual_c == val_c or actual_c.startswith(val_c + "-")
    return False


CSS_STATE_PSEUDOS = frozenset({
    "hover",
    "active",
    "focus",
    "focus-visible",
    "focus-within",
    "visited",
    "target",
    "fullscreen",
    "modal",
    "popover-open",
    "checked",
    "indeterminate",
    "default",
    "disabled",
    "enabled",
    "required",
    "optional",
    "read-only",
    "read-write",
    "placeholder-shown",
    "valid",
    "invalid",
    "user-invalid",
    "in-range",
    "out-of-range",
    "dir",
    "lang",
    "playing",
    "paused",
    "autofill",
})
CSS_KNOWN_PSEUDOS = CSS_STATE_PSEUDOS | {
    "not",
    "is",
    "where",
    "has",
    "root",
    "empty",
    "scope",
    "defined",
    "host",
    "first-child",
    "last-child",
    "only-child",
    "nth-child",
    "nth-last-child",
    "first-of-type",
    "last-of-type",
    "only-of-type",
    "nth-of-type",
    "nth-last-of-type",
    "first-letter",
    "first-line",
    "before",
    "after",
    "marker",
    "selection",
    "placeholder",
    "backdrop",
    "file-selector-button",
    "link",
    "any-link",
    "local-link",
}


def _subject_syntax_ok(subject: str) -> bool:
    """False for empty/malformed #id, .class, or [] attribute selectors."""
    text = subject.strip()
    if not text:
        return True
    i = 0
    n = len(text)
    if text[0] == "*":
        i = 1
    elif text[0].isalpha() or text[0] in "_-":
        while i < n and (text[i].isalnum() or text[i] in "-_\\"):
            i += 1
    while i < n:
        ch = text[i]
        if ch == "#":
            i += 1
            start = i
            while i < n and text[i] not in ".#[":
                i += 1
            if i == start:
                return False
        elif ch == ".":
            i += 1
            start = i
            while i < n and text[i] not in ".#[":
                i += 1
            if i == start:
                return False
        elif ch == "[":
            j = i + 1
            quote = None
            while j < n:
                cj = text[j]
                if quote:
                    if cj == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if cj == quote:
                        quote = None
                    j += 1
                    continue
                if cj in "\"'":
                    quote = cj
                    j += 1
                    continue
                if cj == "]":
                    break
                j += 1
            if j >= n or text[j] != "]":
                return False
            inner = text[i + 1 : j].strip()
            if not inner:
                return False
            spec = inner
            flag_m = re.search(r"\s+([iIsS])\s*$", spec)
            if flag_m:
                spec = spec[: flag_m.start()].rstrip()
            if not re.match(r"^([A-Za-z_:][\w:.-]*)\s*(?:(~=|\|=|\^=|\$=|\*=|=)\s*(.+))?$", spec):
                return False
            i = j + 1
        else:
            return False
    return True


def selector_is_valid(selector: str) -> bool:
    """False when a style-rule selector contains an unknown/malformed compound."""
    chain = split_selector_chain(selector.strip())
    if not chain:
        return False
    for _comb, compound in chain:
        if not compound:
            return False
        for name, _arg, _is_element, malformed in iter_compound_pseudos(compound):
            if malformed or not name:
                return False
            if name not in CSS_KNOWN_PSEUDOS and not name.startswith("-"):
                return False
        if not _subject_syntax_ok(strip_css_pseudos(compound)):
            return False
    return True


def iter_compound_pseudos(compound: str):
    """Yield (name, arg_or_none, is_element, malformed) for :pseudo / ::pseudo."""
    depth_brack = 0
    quote = None
    i = 0
    n = len(compound)
    while i < n:
        ch = compound[i]
        if quote:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            i += 1
            continue
        if ch == "[":
            depth_brack += 1
        elif ch == "]" and depth_brack:
            depth_brack -= 1
        elif ch == ":" and depth_brack == 0:
            i += 1
            is_element = False
            if i < n and compound[i] == ":":
                is_element = True
                i += 1
            start = i
            while i < n and (compound[i].isalnum() or compound[i] == "-"):
                i += 1
            name = compound[start:i].lower()
            arg = None
            if i < n and compound[i] == "(":
                i += 1
                arg_start = i
                depth = 1
                quote2 = None
                closed = False
                while i < n and depth:
                    cj = compound[i]
                    if quote2:
                        if cj == "\\" and i + 1 < n:
                            i += 2
                            continue
                        if cj == quote2:
                            quote2 = None
                        i += 1
                        continue
                    if cj in "\"'":
                        quote2 = cj
                    elif cj == "(":
                        depth += 1
                    elif cj == ")":
                        depth -= 1
                        if depth == 0:
                            arg = compound[arg_start:i]
                            i += 1
                            closed = True
                            break
                    i += 1
                if not closed:
                    yield name, None, is_element, True
                    return
            yield name, arg, is_element, False
            continue
        i += 1


def _selector_list_match_state(arg: str, tag: str, attrs, *, ctx: dict | None = None) -> bool | None:
    """True/False when every selector is a simple compound; None if unevaluable."""
    saw_true = False
    parts = split_selector_list(arg)
    if not parts:
        return None
    for sel in parts:
        chain = split_selector_chain(sel)
        if len(chain) != 1 or chain[0][0]:
            return None
        state = css_compound_match_state(chain[0][1], tag, attrs, ctx=ctx)
        if state is None:
            return None
        if state:
            saw_true = True
    return saw_true


def css_attr_pseudo_matches(name: str, tag: str, attrs) -> bool | None:
    """True/False when the pseudo is attribute-backed; None if it is dynamic."""
    has = lambda key: any(attr.lower() == key for attr, _ in attrs)
    if name == "disabled":
        return has("disabled")
    if name == "enabled":
        return tag in FORM_CTRL_TAGS and not has("disabled")
    if name == "checked":
        if tag == "option":
            return has("selected")
        return has("checked")
    if name == "required":
        return has("required")
    if name == "optional":
        return tag in FORM_CTRL_TAGS and not has("required")
    if name == "read-only":
        if has("readonly"):
            return True
        if any(
            key.lower() == "contenteditable" and (value or "").lower() not in {"false", "inherit"}
            for key, value in attrs
        ):
            return False
        if tag in {"input", "textarea"}:
            return False
        return True
    if name == "read-write":
        if has("readonly"):
            return False
        if tag in {"input", "textarea"}:
            return True
        return any(
            key.lower() == "contenteditable" and (value or "").lower() not in {"false", "inherit"}
            for key, value in attrs
        )
    if name in {"link", "any-link"}:
        if tag not in {"a", "area", "link"}:
            return False
        return has("href")
    return None


def _nth_matches(expr: str | None, index: int) -> bool | None:
    if not expr:
        return None
    text = re.sub(r"\s+", "", expr.lower())
    if text == "odd":
        return index % 2 == 1
    if text == "even":
        return index % 2 == 0
    m = re.fullmatch(r"([+-]?)(\d*)n([+-]\d+)?", text)
    if m:
        sign, step, offset = m.group(1), m.group(2), m.group(3)
        if step == "":
            a = -1 if sign == "-" else 1
        else:
            a = int(f"{sign}{step}")
        b = int(offset) if offset else 0
        if a == 0:
            return index == b
        n, rem = divmod(index - b, a)
        return rem == 0 and n >= 0
    if re.fullmatch(r"[+-]?\d+", text):
        return index == int(text)
    return None


def _structural_pseudo_matches(name: str, arg: str | None, tag: str, ctx: dict) -> bool | None:
    prev = ctx.get("prev_siblings") or []
    empty = ctx.get("empty")
    is_last = ctx.get("is_last")
    ancestors = ctx.get("ancestors") or []
    if name == "empty":
        if empty is None:
            return None
        return bool(empty)
    if name == "root":
        return not ancestors
    if name == "first-child":
        return not prev
    following = ctx.get("following_siblings")
    if name == "last-child":
        if following is not None:
            return not following
        if is_last is None:
            return None
        return bool(is_last)
    if name == "only-child":
        last = (not following) if following is not None else is_last
        if last is None:
            return None
        return (not prev) and bool(last)
    if name == "nth-child":
        return _nth_matches(arg, len(prev) + 1)
    if name == "nth-last-child":
        if following is None:
            return None
        return _nth_matches(arg, len(following) + 1)
    if name == "first-of-type":
        return not any(item[0] == tag for item in prev)
    if name == "last-of-type":
        if following is None:
            return None
        return not any(item[0] == tag for item in following)
    if name == "only-of-type":
        if following is None:
            return None
        return (not any(item[0] == tag for item in prev)) and (
            not any(item[0] == tag for item in following)
        )
    if name == "nth-of-type":
        return _nth_matches(arg, 1 + sum(1 for item in prev if item[0] == tag))
    if name == "nth-last-of-type":
        if following is None:
            return None
        return _nth_matches(arg, 1 + sum(1 for item in following if item[0] == tag))
    return None


def css_pseudos_state(compound: str, tag: str, attrs, *, ctx: dict | None = None) -> bool | None:
    """True if all pseudos are satisfied, False if not, None if unevaluable."""
    ctx = ctx or {}
    for name, arg, is_element, malformed in iter_compound_pseudos(compound):
        if malformed or is_element:
            return None
        if name in CSS_STATE_PSEUDOS or name in {"link", "any-link"}:
            attr_state = css_attr_pseudo_matches(name, tag, attrs)
            if attr_state is True:
                continue
            if attr_state is False:
                return False
            if name in CSS_STATE_PSEUDOS:
                return False
            return None
        if name in {"not", "is", "where"}:
            if arg is None:
                return None
            inner = _selector_list_match_state(arg, tag, attrs, ctx=ctx)
            if inner is None:
                return None
            if name == "not":
                if inner:
                    return False
            elif not inner:
                return False
            continue
        struct = _structural_pseudo_matches(name, arg, tag, ctx)
        if struct is True:
            continue
        if struct is False:
            return False
        return None
    return True


def css_static_pseudos_ok(compound: str) -> bool:
    """False when the compound has a state pseudo-class the static preview cannot satisfy."""
    for name, _arg, is_element, malformed in iter_compound_pseudos(compound):
        if malformed or is_element:
            return False
        if name in CSS_STATE_PSEUDOS:
            return False
    return True


def _css_subject_matches(subject: str, tag: str, attrs) -> bool:
    if not subject:
        return False
    if subject == "*":
        return True
    ad = {name.lower(): (value or "") for name, value in attrs}
    i = 0
    n = len(subject)
    named = re.match(r"^[a-zA-Z][a-zA-Z0-9-]*", subject)
    if named:
        if decode_css_escapes(named.group(0)).lower() != tag:
            return False
        i = named.end()
    elif n == 0 or subject[0] not in "#.[":
        return False
    while i < n:
        ch = subject[i]
        if ch == "#":
            j = i + 1
            while j < n and subject[j] not in ".#[":
                j += 1
            if ad.get("id") != decode_css_escapes(subject[i + 1 : j]):
                return False
            i = j
        elif ch == ".":
            j = i + 1
            while j < n and subject[j] not in ".#[":
                j += 1
            if decode_css_escapes(subject[i + 1 : j]) not in ad.get("class", "").split():
                return False
            i = j
        elif ch == "[":
            j = i + 1
            quote = None
            while j < n:
                cj = subject[j]
                if quote:
                    if cj == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if cj == quote:
                        quote = None
                    j += 1
                    continue
                if cj in "\"'":
                    quote = cj
                    j += 1
                    continue
                if cj == "]":
                    break
                j += 1
            if j >= n or subject[j] != "]":
                return False
            inner = subject[i + 1 : j].strip()
            if not css_attr_selector_matches(inner, ad):
                return False
            i = j + 1
        else:
            return False
    return True


def css_compound_match_state(compound: str, tag: str, attrs, *, ctx: dict | None = None) -> bool | None:
    pseudo = css_pseudos_state(compound, tag, attrs, ctx=ctx)
    if pseudo is not True:
        return pseudo
    subject = strip_css_pseudos(compound)
    if subject == "*":
        return True
    if subject:
        return True if _css_subject_matches(subject, tag, attrs) else False
    names = [name for name, _arg, _el, _bad in iter_compound_pseudos(compound)]
    if names:
        return True
    return False


def css_compound_matches(compound: str, tag: str, attrs, *, ctx: dict | None = None) -> bool:
    state = css_compound_match_state(compound, tag, attrs, ctx=ctx)
    return state is True


def _ancestor_ctx(anc, ancestors_prefix) -> dict:
    following = anc[3] if len(anc) > 3 else None
    return {
        "prev_siblings": anc[2],
        "ancestors": ancestors_prefix,
        "empty": None,
        "is_last": None if following is None else (not following),
        "following_siblings": following,
    }


def _css_match_chain(
    compounds: list[str],
    combs: list[str],
    tag: str,
    attrs,
    ancestors: list,
    prev_siblings: list[tuple[str, object]],
    ctx: dict | None = None,
) -> bool:
    if not compounds:
        return False
    subject_ctx = ctx or {
        "prev_siblings": prev_siblings,
        "ancestors": ancestors,
        "empty": None,
        "is_last": None,
    }
    if not css_compound_matches(compounds[-1], tag, attrs, ctx=subject_ctx):
        return False
    if len(compounds) == 1:
        return True
    comb = combs[-1]
    left_compounds = compounds[:-1]
    left_combs = combs[:-1]
    if comb == ">":
        if not ancestors:
            return False
        ptag, pattrs, pprev = ancestors[-1][0], ancestors[-1][1], ancestors[-1][2]
        return _css_match_chain(
            left_compounds,
            left_combs,
            ptag,
            pattrs,
            ancestors[:-1],
            pprev,
            _ancestor_ctx(ancestors[-1], ancestors[:-1]),
        )
    if comb == " ":
        for j in range(len(ancestors) - 1, -1, -1):
            atag, aattrs, aprev = ancestors[j][0], ancestors[j][1], ancestors[j][2]
            if _css_match_chain(
                left_compounds,
                left_combs,
                atag,
                aattrs,
                ancestors[:j],
                aprev,
                _ancestor_ctx(ancestors[j], ancestors[:j]),
            ):
                return True
        return False
    if comb == "+":
        if not prev_siblings:
            return False
        stag, sattrs = prev_siblings[-1]
        return _css_match_chain(left_compounds, left_combs, stag, sattrs, ancestors, prev_siblings[:-1])
    if comb == "~":
        for j in range(len(prev_siblings) - 1, -1, -1):
            stag, sattrs = prev_siblings[j]
            if _css_match_chain(left_compounds, left_combs, stag, sattrs, ancestors, prev_siblings[:j]):
                return True
        return False
    return False


def css_selector_matches(
    selector: str,
    tag: str,
    attrs,
    ancestors: list[tuple[str, object, list]] | None = None,
    prev_siblings: list[tuple[str, object]] | None = None,
    *,
    empty: bool | None = None,
    is_last: bool | None = None,
    following_siblings: list[tuple[str, object]] | None = None,
) -> bool:
    """Match a simple CSS selector against the current element and its ancestors."""
    chain = split_selector_chain(selector)
    if not chain:
        return False
    compounds = [part[1] for part in chain]
    combs = [part[0] for part in chain[1:]]
    ancs = list(ancestors or [])
    prev = list(prev_siblings or [])
    ctx = {
        "prev_siblings": prev,
        "ancestors": ancs,
        "empty": empty,
        "is_last": is_last,
        "following_siblings": following_siblings,
    }
    return _css_match_chain(compounds, combs, tag, attrs, ancs, prev, ctx)


class PreviewMarkerCollector(HTMLParser):
    """Collect contiguous visible text and intended attributes; skip hidden subtrees."""

    def __init__(self, sheet_hides: list[tuple[str, dict[str, tuple[str, bool]], int | None]] | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool, bool, bool, bool]] = []
        self.skip_depth = 0
        self.vis_hidden_stack: list[bool] = []
        self.text_buf: list[str] = []
        self.chunks: list[str] = []
        self.details_stack: list[dict[str, bool]] = []
        self.sheet_hides = sheet_hides or []
        self.dom_open: list[tuple[str, object, list]] = []
        self.level_children: list[list[tuple[str, object]]] = [[]]
        self.open_meta: list[dict] = []

    def _flush_text(self) -> None:
        if self.text_buf:
            self.chunks.append("".join(self.text_buf))
            self.text_buf.clear()

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_starttag(self, tag: str, attrs) -> None:
        ltag = html_tag_name(tag)
        self._open(ltag, attrs)
        if ltag in VOID_TAGS:
            self.handle_endtag(ltag)

    def _pop_implied(self, targets: set[str], stop: frozenset[str]) -> None:
        if not targets:
            return
        has_target = False
        for tag, *_rest in reversed(self.stack):
            if tag in stop:
                break
            if tag in targets:
                has_target = True
                break
        if not has_target:
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in stop:
                return
            self.handle_endtag(top)
            if top in targets:
                return

    def _implied_close(self, incoming: str) -> None:
        if incoming in P_CLOSING_START:
            self._pop_implied({"p"}, IMPLIED_END_STOP)
        targets = set(IMPLIED_END_ON_START.get(incoming, ()))
        if not targets:
            return
        stop = LIST_ITEM_SCOPE_STOP if incoming == "li" else IMPLIED_END_STOP
        self._pop_implied(targets, stop)

    def _close_nested_anchor(self, incoming: str) -> None:
        if incoming != "a":
            return
        if not any(tag == "a" for tag, *_rest in self.stack):
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in {"html", "body", "table", "thead", "tbody", "tfoot", "tr", "td", "th", "template"}:
                return
            self.handle_endtag(top)
            if top == "a":
                return

    def _clear_table_stack(self, incoming: str) -> None:
        if incoming in TABLE_SECTION:
            while self.stack:
                top = self.stack[-1][0]
                if top in {"table", "html", "body", "template"}:
                    break
                self.handle_endtag(top)
                if top in TABLE_SECTION:
                    break
        if incoming not in TABLE_START:
            return
        if not any(tag == "table" for tag, *_rest in self.stack):
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in TABLE_CONTEXT:
                return
            self.handle_endtag(top)

    def _sheet_hide(
        self,
        tag: str,
        attrs,
        *,
        empty: bool | None = None,
        is_last: bool | None = None,
        ancestors: list | None = None,
        prev_siblings: list | None = None,
        following_siblings: list | None = None,
    ) -> tuple[bool, bool, bool, bool, str | None, bool]:
        ancestors = list(self.dom_open) if ancestors is None else ancestors
        prev_siblings = list(self.level_children[-1]) if prev_siblings is None else prev_siblings
        winning: dict[str, tuple[str, bool, int | None, tuple[int, int, int], int]] = {}
        for order, (selector, decls, layer_index) in enumerate(self.sheet_hides):
            if not css_selector_matches(
                selector,
                tag,
                attrs,
                ancestors,
                prev_siblings,
                empty=empty,
                is_last=is_last,
                following_siblings=following_siblings,
            ):
                continue
            spec = css_specificity(selector)
            for prop, (token, imp) in decls.items():
                prev = winning.get(prop)
                if prev is None:
                    winning[prop] = (token, imp, layer_index, spec, order)
                    continue
                _tok, p_imp, p_layer, p_spec, p_ord = prev
                if imp != p_imp:
                    if imp:
                        winning[prop] = (token, imp, layer_index, spec, order)
                    continue
                layer_rank = _cascade_layer_beats(imp, layer_index, p_layer)
                if layer_rank is True:
                    winning[prop] = (token, imp, layer_index, spec, order)
                    continue
                if layer_rank is False:
                    continue
                if spec > p_spec or (spec == p_spec and order >= p_ord):
                    winning[prop] = (token, imp, layer_index, spec, order)
        disp, disp_imp = winning.get("display", ("", False, (0, 0, 0), -1))[:2]
        opac, opac_imp = winning.get("opacity", ("", False, (0, 0, 0), -1))[:2]
        vis_tok, vis_imp = winning.get("visibility", ("", False, (0, 0, 0), -1))[:2]
        vis = vis_tok if vis_tok in {"hidden", "collapse", "visible"} else None
        return disp == "none", disp_imp, _opacity_is_zero(opac), opac_imp, vis, vis_imp

    def _sheet_hides_element(self, disp_none: bool, opac0: bool, vis: str | None) -> bool:
        return disp_none or opac0 or vis in {"hidden", "collapse"}

    def _effective_hidden(
        self,
        tag: str,
        attrs,
        *,
        empty: bool | None = None,
        is_last: bool | None = None,
        ancestors: list | None = None,
        prev_siblings: list | None = None,
        following_siblings: list | None = None,
    ) -> bool:
        sheet_display_none, sheet_display_imp, sheet_opacity_zero, sheet_opacity_imp, sheet_vis, sheet_vis_imp = (
            self._sheet_hide(
                tag,
                attrs,
                empty=empty,
                is_last=is_last,
                ancestors=ancestors,
                prev_siblings=prev_siblings,
                following_siblings=following_siblings,
            )
        )
        style = next((value or "" for name, value in attrs if name.lower() == "style"), "")
        inline_decls = winning_style_decls(style)

        def cascade_hide(sheet_on: bool, sheet_imp: bool, prop: str, hides) -> bool:
            if prop not in inline_decls:
                return sheet_on
            token, imp = inline_decls[prop]
            if sheet_on and sheet_imp and not imp:
                return True
            return hides(token)

        display_none = cascade_hide(sheet_display_none, sheet_display_imp, "display", lambda t: t == "none")
        opacity_zero = cascade_hide(sheet_opacity_zero, sheet_opacity_imp, "opacity", _opacity_is_zero)
        if "visibility" in inline_decls:
            token, imp = inline_decls["visibility"]
            if sheet_vis in {"hidden", "collapse"} and sheet_vis_imp and not imp:
                vis = sheet_vis
            else:
                vis = token if token in {"hidden", "visible", "collapse"} else None
        else:
            vis = sheet_vis
        return self._sheet_hides_element(display_none, opacity_zero, vis)

    def _drop_chunk_range(self, start: int, end: int) -> None:
        if start < 0:
            start = 0
        if end > len(self.chunks):
            end = len(self.chunks)
        if start < end:
            self.chunks = self.chunks[:start] + self.chunks[end:]

    def _patch_ancestor_following(self, meta: dict, ancestor_attrs, following: list) -> None:
        ancs = list(meta.get("ancestors") or [])
        patched: list = []
        for anc in ancs:
            if len(anc) >= 2 and anc[1] is ancestor_attrs:
                patched.append((anc[0], anc[1], anc[2], following))
            else:
                patched.append(anc)
        meta["ancestors"] = patched
        for child in meta.get("child_metas") or []:
            self._patch_ancestor_following(child, ancestor_attrs, following)

    def _rehide_subtree(self, node: dict, following: list) -> None:
        if not node.get("skip"):
            empty = not node.get("had_text") and not node.get("had_element")
            if self._effective_hidden(
                node["tag"],
                node["attrs"],
                empty=empty,
                is_last=not following,
                following_siblings=following,
                ancestors=node.get("ancestors"),
                prev_siblings=node.get("prev"),
            ):
                self._drop_chunk_range(node.get("chunk_at", 0), node.get("chunk_end", 0))
                return
        kids = list(node.get("child_metas") or [])
        sibs = [(child["tag"], child["attrs"]) for child in kids]
        for child in reversed(kids):
            idx = len(child.get("prev") or [])
            child_following = sibs[idx + 1 :] if idx + 1 <= len(sibs) else []
            child["following"] = child_following
            for desc in child.get("child_metas") or []:
                self._patch_ancestor_following(desc, child["attrs"], child_following)
            self._rehide_subtree(child, child_following)

    def _hide_children_by_final_siblings(self, parent_meta: dict, siblings: list) -> None:
        """Re-evaluate reverse-position pseudos once a parent's children are complete."""
        children = list(parent_meta.get("child_metas") or [])
        for child in reversed(children):
            idx = len(child.get("prev") or [])
            following = siblings[idx + 1 :] if idx + 1 <= len(siblings) else []
            child["following"] = following
            for desc in child.get("child_metas") or []:
                self._patch_ancestor_following(desc, child["attrs"], following)
            self._rehide_subtree(child, following)

    def _open(self, tag: str, attrs) -> None:
        ltag = tag.lower()
        if ltag in TABLE_START and not any(item[0] == "table" for item in self.stack):
            return
        self._implied_close(ltag)
        self._close_nested_anchor(ltag)
        self._clear_table_stack(ltag)
        hidden = any(name.lower() == "hidden" for name, _ in attrs)
        style = next((value or "" for name, value in attrs if name.lower() == "style"), "")
        inline_decls = winning_style_decls(style)

        def cascade_hide(sheet_on: bool, sheet_imp: bool, prop: str, hides) -> bool:
            if prop not in inline_decls:
                return sheet_on
            token, imp = inline_decls[prop]
            if sheet_on and sheet_imp and not imp:
                return True
            return hides(token)

        empty_now = True if ltag in VOID_TAGS else None
        sheet_display_none, sheet_display_imp, sheet_opacity_zero, sheet_opacity_imp, sheet_vis, sheet_vis_imp = (
            self._sheet_hide(ltag, attrs, empty=empty_now)
        )
        display_none = cascade_hide(sheet_display_none, sheet_display_imp, "display", lambda t: t == "none")
        opacity_zero = cascade_hide(sheet_opacity_zero, sheet_opacity_imp, "opacity", _opacity_is_zero)
        hard = hidden or display_none or opacity_zero
        if ltag == "input" and any(value.lower() == "hidden" for value in attr_values(attrs, "type")):
            hard = True
        if ltag == "dialog" and not any(name.lower() == "open" for name, _ in attrs):
            hard = True
        if any(name.lower() == "popover" for name, _ in attrs):
            hard = True
        state = self.details_stack[-1] if self.details_stack else None
        parent_tag = self.stack[-1][0] if self.stack else None
        is_first_summary = (
            ltag == "summary"
            and state is not None
            and parent_tag == "details"
            and not state["in_summary"]
            and not state["used_summary"]
        )
        hide_for_details = state is not None and not state["in_summary"] and not is_first_summary
        hard = self.skip_depth > 0 or ltag in PREVIEW_SKIP_TAGS or hard or hide_for_details
        parent_vis_hidden = self.vis_hidden_stack[-1] if self.vis_hidden_stack else False
        if "visibility" in inline_decls:
            token, imp = inline_decls["visibility"]
            if sheet_vis in {"hidden", "collapse"} and sheet_vis_imp and not imp:
                own_vis = sheet_vis
            else:
                own_vis = token if token in {"hidden", "visible", "collapse"} else None
        else:
            own_vis = sheet_vis
        if own_vis in {"hidden", "collapse"}:
            vis_hidden = True
        elif own_vis == "visible":
            vis_hidden = False
        else:
            vis_hidden = parent_vis_hidden
        self.vis_hidden_stack.append(vis_hidden)
        skip = hard or vis_hidden
        if ltag in PREVIEW_BLOCK_BREAK and self.skip_depth == 0:
            self._flush_text()
        opened_closed_details = ltag == "details" and not any(name.lower() == "open" for name, _ in attrs)
        opened_summary = False
        if is_first_summary and state is not None:
            state["in_summary"] = True
            state["used_summary"] = True
            opened_summary = True
        if opened_closed_details:
            self.details_stack.append({"in_summary": False, "used_summary": False})
        fallback = False
        if hard:
            self.skip_depth += 1
        elif not vis_hidden and ltag in PREVIEW_FALLBACK_TAGS:
            self.skip_depth += 1
            fallback = True
        if self.open_meta:
            self.open_meta[-1]["had_element"] = True
        chunk_at = len(self.chunks)
        parent_anc = list(self.dom_open)
        prev = list(self.level_children[-1])
        self.stack.append((ltag, skip, hard, opened_closed_details, opened_summary, fallback))
        self.level_children[-1].append((ltag, attrs))
        self.dom_open.append((ltag, attrs, prev, None))
        self.level_children.append([])
        self.open_meta.append({
            "chunk_at": chunk_at,
            "had_text": False,
            "had_element": False,
            "tag": ltag,
            "attrs": attrs,
            "skip": skip,
            "ancestors": parent_anc,
            "prev": prev,
            "child_metas": [],
        })
        if hard or vis_hidden:
            return
        for name, value in attrs:
            if not value:
                continue
            lname = name.lower()
            if lname in PREVIEW_MARKER_ATTRS or lname.startswith("data-"):
                self.chunks.append(value)

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if end_tag_matches(self.stack[i][0], ltag):
                if ltag in PREVIEW_BLOCK_BREAK and self.skip_depth == 0:
                    self._flush_text()
                for _, _was_skip, was_hard, opened_closed_details, opened_summary, was_fallback in reversed(self.stack[i:]):
                    meta = self.open_meta.pop() if self.open_meta else None
                    siblings = list(self.level_children[-1]) if self.level_children else []
                    if meta:
                        self._hide_children_by_final_siblings(meta, siblings)
                    if meta and not meta["skip"]:
                        empty = not meta["had_text"] and not meta["had_element"]
                        if empty:
                            if self._effective_hidden(
                                meta["tag"],
                                meta["attrs"],
                                empty=True,
                                ancestors=meta["ancestors"],
                                prev_siblings=meta["prev"],
                                following_siblings=meta.get("following"),
                                is_last=None if meta.get("following") is None else not meta.get("following"),
                            ):
                                self.chunks = self.chunks[: meta["chunk_at"]]
                    if meta is not None:
                        meta["chunk_end"] = len(self.chunks)
                        if self.open_meta:
                            self.open_meta[-1].setdefault("child_metas", []).append(meta)
                    if opened_summary and self.details_stack:
                        self.details_stack[-1]["in_summary"] = False
                    if opened_closed_details and self.details_stack:
                        self.details_stack.pop()
                    if was_hard or was_fallback:
                        self.skip_depth = max(0, self.skip_depth - 1)
                    if self.vis_hidden_stack:
                        self.vis_hidden_stack.pop()
                    if self.dom_open:
                        self.dom_open.pop()
                    if len(self.level_children) > 1:
                        self.level_children.pop()
                del self.stack[i:]
                return
        if ltag == "br":
            self.handle_starttag("br", [])
            return
        if ltag == "p":
            self.handle_starttag("p", [])
            self.handle_endtag("p")

    def handle_data(self, data: str) -> None:
        if self.open_meta:
            self.open_meta[-1]["had_text"] = True
        if self.skip_depth:
            return
        if self.vis_hidden_stack and self.vis_hidden_stack[-1]:
            return
        self.text_buf.append(data)

    def handle_comment(self, _data: str) -> None:
        return


def collect_preview_marker_text(preview: str) -> list[str]:
    collector = PreviewMarkerCollector(extract_stylesheet_hide_rules(preview))
    try:
        collector.feed(preview)
        collector.close()
    except Exception:  # noqa: BLE001
        return []
    collector._flush_text()
    return collector.chunks


def preview_shows_marker(preview: str, ident: str, *prefixes: str) -> bool:
    for chunk in collect_preview_marker_text(preview):
        if has_preview_marker(chunk, ident, *prefixes):
            return True
    return False


def iter_top_level_fences(text: str):
    lines = text.splitlines(keepends=True)
    pos = 0
    opener: tuple[int, str, str] | None = None
    html_blocks = HtmlBlockScanner()
    for line in lines:
        raw = line.rstrip("\r\n")
        if opener is not None:
            start, marker, info = opener
            close = FENCE_CLOSE.match(raw)
            if close and close.group(1)[0] == marker[0] and len(close.group(1)) >= len(marker):
                yield {"start": start, "end": pos + len(line), "marker": marker, "info": info}
                opener = None
            pos += len(line)
            continue
        if html_blocks.in_block(raw):
            pos += len(line)
            continue
        open_m = FENCE_OPEN.match(raw)
        if open_m:
            marker, info = open_m.group(1), open_m.group(2)
            if marker.startswith("`") and "`" in info:
                pos += len(line)
                continue
            opener = (pos, marker, info.strip())
        pos += len(line)
    if opener is not None:
        start, marker, info = opener
        yield {"start": start, "end": len(text), "marker": marker, "info": info}


def unfenced_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    last = 0
    for fence in iter_top_level_fences(text):
        if last < fence["start"]:
            spans.append((last, fence["start"]))
        last = fence["end"]
    if last < len(text):
        spans.append((last, len(text)))
    return spans


def _in_spans(pos: int, spans: list[tuple[int, int]]) -> bool:
    return any(start <= pos < end for start, end in spans)


def html_block_line_starts(text: str) -> set[int]:
    """Start offsets of unfenced lines consumed by CommonMark HTML blocks."""
    spans = unfenced_spans(text)
    scanner = HtmlBlockScanner()
    blocked: set[int] = set()
    pos = 0
    for line in text.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        if _in_spans(pos, spans) and scanner.in_block(raw):
            blocked.add(pos)
        pos += len(line)
    return blocked


def unfenced_markdown(text: str) -> str:
    pieces: list[str] = []
    last = 0
    for fence in iter_top_level_fences(text):
        pieces.append(text[last : fence["start"]])
        pieces.append("\n")
        last = fence["end"]
    pieces.append(text[last:])
    return "".join(pieces)


def fence_inner_html(text: str, fence: dict) -> str:
    chunk = text[fence["start"] : fence["end"]]
    lines = chunk.splitlines(keepends=True)
    if len(lines) < 2:
        return ""
    closer = FENCE_CLOSE.match(lines[-1].rstrip("\r\n"))
    inner = lines[1:-1] if closer else lines[1:]
    return "".join(inner)


def html_fence_bodies(text: str, start: int, end: int) -> list[str]:
    bodies: list[str] = []
    for fence in iter_top_level_fences(text):
        if fence["start"] < start or fence["end"] > end:
            continue
        info = fence["info"].split()[0].lower() if fence["info"] else ""
        if info == "html":
            bodies.append(fence_inner_html(text, fence))
    return bodies


def _has_heading_line(md_text: str, heading: str) -> bool:
    return bool(re.search(rf"(?m)^{re.escape(heading)}\s*$", md_text))


def _md_section(md_text: str, heading: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", md_text)
    if not match:
        return None
    rest = md_text[match.end() :]
    nxt = re.search(r"(?m)^## ", rest)
    if nxt:
        return md_text[match.start() : match.end() + nxt.start()]
    return md_text[match.start() :]


def iter_component_regions(md_text: str):
    spans = unfenced_spans(md_text)
    html_lines = html_block_line_starts(md_text)
    for match in COMPONENT_HEADING.finditer(md_text):
        if not _in_spans(match.start(), spans):
            continue
        if match.start() in html_lines:
            continue
        region_start = match.end()
        nxt = None
        for nxt_match in re.finditer(r"(?m)^#{2,3} ", md_text[region_start:]):
            abs_pos = region_start + nxt_match.start()
            if not _in_spans(abs_pos, spans):
                continue
            line = md_text[abs_pos:].splitlines()[0] if md_text[abs_pos:] else ""
            # Ignore ##/### inside raw HTML, except a later ### slot:/sig: so we
            # do not steal that component's fence after the HTML block ends.
            if abs_pos in html_lines and not COMPONENT_HEADING.match(line):
                continue
            nxt = nxt_match
            break
        region_end = region_start + nxt.start() if nxt else len(md_text)
        yield match.group(0).strip(), match.group(1), match.group(2), region_start, region_end


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
        self._open(tag, attrs, void=tag.lower() in VOID_TAGS)

    def handle_starttag(self, tag: str, attrs) -> None:
        self._open(tag, attrs, void=tag.lower() in VOID_TAGS)

    def _pop_implied(self, targets: set[str], stop: frozenset[str]) -> None:
        if not targets:
            return
        has_target = False
        for tag, *_rest in reversed(self.stack):
            if tag in stop:
                break
            if tag in targets:
                has_target = True
                break
        if not has_target:
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in stop:
                return
            self.handle_endtag(top)
            if top in targets:
                return

    def _implied_close(self, incoming: str) -> None:
        if incoming in P_CLOSING_START:
            self._pop_implied({"p"}, IMPLIED_END_STOP)
        targets = set(IMPLIED_END_ON_START.get(incoming, ()))
        if not targets:
            return
        stop = LIST_ITEM_SCOPE_STOP if incoming == "li" else IMPLIED_END_STOP
        self._pop_implied(targets, stop)

    def _close_nested_anchor(self, incoming: str) -> None:
        if incoming != "a":
            return
        if not any(tag == "a" for tag, *_rest in self.stack):
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in {"html", "body", "table", "thead", "tbody", "tfoot", "tr", "td", "th", "template"}:
                return
            self.handle_endtag(top)
            if top == "a":
                return

    def _clear_table_stack(self, incoming: str) -> None:
        if incoming in TABLE_SECTION:
            while self.stack:
                top = self.stack[-1][0]
                if top in {"table", "html", "body", "template"}:
                    break
                self.handle_endtag(top)
                if top in TABLE_SECTION:
                    break
        if incoming not in TABLE_START:
            return
        while self.stack:
            top = self.stack[-1][0]
            if top in TABLE_CONTEXT:
                return
            self.handle_endtag(top)

    def _open(self, tag: str, attrs, *, void: bool) -> None:
        ltag = html_tag_name(tag)
        if ltag in TABLE_START and not any(item[0] == "table" for item in self.stack):
            return
        void = ltag in VOID_TAGS
        self._implied_close(ltag)
        self._close_nested_anchor(ltag)
        self._clear_table_stack(ltag)
        ad = {k.lower(): v for k, v in attrs}
        at_root = not self.stack
        if ltag in FORBIDDEN_THEME_TAGS:
            self._add("ERROR", f"{self.label}: {FORBIDDEN_THEME_TAGS[ltag]}")
        if "class" in ad:
            self._add("ERROR", f"{self.label}: 出现 class（交付组件禁止）")
        if "id" in ad:
            self._add("ERROR", f"{self.label}: 出现 id（THEME.md 组件禁止，预览页可用）")
        styles = attr_values(attrs, "style")
        if len(styles) > 1:
            self._add("ERROR", f"{self.label}: 禁止重复 style 属性")
        effective_style = styles[0] if styles else ""
        if ltag in THEME_NEED_STYLE and not has_css_declaration(effective_style):
            self._add("ERROR", f"{self.label}: <{ltag}> 缺少 style")
        if self.label.strip() == "### slot:root" and at_root and ltag == "section":
            if not has_root_layout(effective_style):
                self._add("ERROR", f"{self.label}: 根 section 须含 max-width:677px 与水平 margin:0 auto 的 style")
        if ltag == "img" and not has_responsive_image_style(effective_style):
            self._add("ERROR", f"{self.label}: <img> 须含 max-width:100%;height:auto;display:block;margin:0 auto")
        for name, value in attrs:
            lname = name.lower()
            if lname.startswith("on") and len(lname) > 2:
                self._add("ERROR", f"{self.label}: 禁止事件属性 {lname}")
            if lname in URL_ATTRS and is_executable_url(value or ""):
                self._add("ERROR", f"{self.label}: 禁止可执行 URL")
        for style in attr_values(attrs, "style"):
            stripped = normalize_style(style)
            normalized = SCHEME_IGNORED.sub("", stripped)
            if stripped and (EXEC_IN_STYLE.search(stripped) or EXEC_IN_STYLE.search(normalized)):
                self._add("ERROR", f"{self.label}: style 含可执行内容")
            for rx, msg in THEME_STYLE_CHECKS:
                if rx.search(stripped):
                    self._add("ERROR", f"{self.label}: {msg}")
            for token in font_size_limit_hits(style):
                self._add("ERROR", f"{self.label}: font-size {token} 超过 24px")
            if FOURSIDE_DASHED.search(stripped):
                self._has_dashed = True
            if CENTERED.search(stripped):
                self._has_center = True
        is_leaf = ltag == "span" and "leaf" in ad
        if is_leaf:
            self.leaf_depth += 1
        if self.leaf_depth and ltag in LEAF_BLOCK_TAGS:
            self._add("ERROR", f"{self.label}: span[leaf] 内出现块级标签")
        if not void:
            self.stack.append((ltag, is_leaf))

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        matched = False
        for i in range(len(self.stack) - 1, -1, -1):
            if end_tag_matches(self.stack[i][0], ltag):
                matched = True
                for _, was_leaf in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                del self.stack[i:]
                break
        if not matched and ltag == "p":
            self._open("p", [], void=False)
            self.handle_endtag("p")
            return
        if not matched and ltag == "br":
            self._open("br", [], void=True)
            return
        if not matched and ltag in FORBIDDEN_THEME_TAGS:
            self._add("ERROR", f"{self.label}: {FORBIDDEN_THEME_TAGS[ltag]}")

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


THEME_RAW_UNSAFE = [
    (re.compile(r"<!\[", re.I), "禁止 CDATA / 不完整声明"),
    (re.compile(r"<script\b", re.I), "出现 <script>"),
    (re.compile(r"<object\b", re.I), "出现禁止标签"),
    (re.compile(r"<embed\b", re.I), "出现禁止标签"),
    (re.compile(r"<meta\b", re.I), "出现禁止标签"),
    (re.compile(r"<base\b", re.I), "出现禁止标签"),
    (re.compile(r"<plaintext\b", re.I), "出现禁止标签"),
    (re.compile(r"<xmp\b", re.I), "出现禁止标签"),
    (re.compile(r"<link\b", re.I), "出现禁止标签"),
    (re.compile(r"<template\b", re.I), "出现禁止标签"),
    (re.compile(r"<select\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<option\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<optgroup\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<dialog\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"<details\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"<noscript\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"<html\b", re.I), "出现 <html>/<head>/<body>，组件须为可粘贴片段"),
    (re.compile(r"<head\b", re.I), "出现 <html>/<head>/<body>，组件须为可粘贴片段"),
    (re.compile(r"<body\b", re.I), "出现 <html>/<head>/<body>，组件须为可粘贴片段"),
    (re.compile(r"<title\b", re.I), "出现 <title>，组件须为可粘贴片段"),
    (re.compile(r"</div\b", re.I), "出现 <div>，请用 <section>"),
]


def lint_html_block(html: str, label: str) -> list[tuple[str, str]]:
    inspector = ThemeHtmlInspector(label)
    for rx, msg in THEME_RAW_UNSAFE:
        if rx.search(html):
            inspector._add("ERROR", f"{label}: {msg}")
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
    if not isinstance(data, dict):
        return errors, warnings

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
        md_source = strip_html_comments(md_text, markdown=True)
        structure_md = visible_structure_markdown(md_text)
        for heading in REQUIRED_MD_HEADINGS:
            if not _has_heading_line(structure_md, heading):
                errors.append(f"THEME.md 缺少章节 {heading}")
        recipe = _md_section(structure_md, "## 文章类型配方")
        if recipe is not None:
            covered = recipe_entry_ids(recipe, set(unique_sigs))
            for kind in ARTICLE_TYPES:
                if kind not in covered:
                    errors.append(f"THEME.md 文章类型配方缺少 {kind}")

        slot_ids = SLOT_HEADING.findall(structure_md)
        for required in REQUIRED_SLOTS:
            if required not in slot_ids:
                errors.append(f"THEME.md 缺少 ### slot:{required}")
        dup = _duplicates(slot_ids)
        if dup:
            errors.append(f"THEME.md 重复槽: {', '.join(dup)}")

        sig_ids = SIG_HEADING.findall(structure_md)
        unique_sig_ids = list(dict.fromkeys(sig_ids))
        sig_dup = _duplicates(sig_ids)
        if sig_dup:
            errors.append(f"THEME.md 重复签名槽: {', '.join(sig_dup)}")
        if len(unique_sig_ids) < 8 or len(unique_sig_ids) > 16:
            errors.append(f"THEME.md 签名槽必须 8–16 个不重复 id，当前 {len(unique_sig_ids)}")
        if sorted(unique_sigs) != sorted(unique_sig_ids):
            errors.append("theme.json signature_slots 与 THEME.md ### sig:* 不一致")

        for label, kind, ident, region_start, region_end in iter_component_regions(md_source):
            fences = [
                body
                for body in html_fence_bodies(md_source, region_start, region_end)
                if html_body_has_element(body)
            ]
            if not fences:
                errors.append(f"{label} 缺少 html 代码块")
                continue
            if len(fences) > 1:
                errors.append(f"{label} 应恰好一个 html 代码块，当前 {len(fences)}")
            for body in fences:
                if not html_fence_usable(body, kind, ident):
                    errors.append(f"{label} html 代码块缺少可用内容")
                for level, msg in lint_html_block(body, label):
                    (errors if level == "ERROR" else warnings).append(msg)

    if not preview_path.is_file():
        errors.append("缺少 preview.html")
    else:
        preview = preview_path.read_text(encoding="utf-8")
        if "<html" not in preview.lower():
            warnings.append("preview.html 不像完整 HTML 文档")
        for slot in REQUIRED_SLOTS:
            if not preview_shows_marker(preview, slot, "slot:", "preview-slot-"):
                errors.append(f"preview.html 未展示 slot:{slot}")
        for sig in unique_sigs:
            if not preview_shows_marker(preview, sig, "sig:", "preview-sig-", "preview-slot-"):
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
