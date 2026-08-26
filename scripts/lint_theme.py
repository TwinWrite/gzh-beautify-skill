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
PREVIEW_ID_TAIL = re.compile(r"[a-z0-9_-]")
RECIPE_LIST = re.compile(r"^(?:[-*+]|\d+[.)])\s+`?([a-z][a-z0-9_-]*)`?\s*[:：]\s*(\S.*)$", re.I)
RECIPE_PLAIN = re.compile(r"^`?([a-z][a-z0-9_-]*)`?\s*[:：]\s*(\S.*)$", re.I)
RECIPE_SLOT = re.compile(
    r"(?<![a-z0-9_-])(?:" + "|".join(re.escape(s) for s in REQUIRED_SLOTS) + r")(?![a-z0-9_-])",
    re.I,
)
RECIPE_SIG = re.compile(r"签名槽|\bsig:|\bsig-[a-z0-9-]+", re.I)
RECIPE_EXCLUDE = re.compile(r"不要用|不要|排除|不用")
HTML_ATTR_NAME = re.compile(r"[A-Za-z_:][A-Za-z0-9_.:-]*")
EXEC_SCHEME = re.compile(
    r"^\s*(?:javascript|vbscript|livescript|mocha)\s*:|"
    r"^\s*data\s*:\s*(?:text\s*/\s*html|text\s*/\s*javascript|application\s*/\s*(?:javascript|ecmascript))",
    re.I,
)
EXEC_IN_STYLE = re.compile(r"javascript\s*:|expression\s*\(|-moz-binding", re.I)

SKIP_TAGS = {"head", "title", "style", "script"}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr", "param"}
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
CSS_IMPORTANT = re.compile(r"!\s*important\s*$", re.I)
_CSS_HEX = frozenset("0123456789abcdefABCDEF")
_CSS_ESCAPE_WS = frozenset(" \t\n\r\f")
HTML_TAG_NAME = re.compile(r"^[a-z][a-z0-9-]*$", re.I)


def html_tag_name(tag: str) -> str:
    ltag = (tag or "").lower()
    return "img" if ltag == "image" else ltag


HTML_COMMENT_OPEN = "<!--"
HTML_COMMENT_CLOSE = "-->"
HTML_BLOCK_OPEN = re.compile(
    r"(?i)^ {0,3}</?(?:address|article|aside|base|basefont|blockquote|body|"
    r"caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|"
    r"figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|"
    r"html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|"
    r"optgroup|option|p|param|section|source|summary|table|tbody|td|"
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
}
PREVIEW_FALLBACK_TAGS = {"iframe", "canvas", "object", "video", "audio"}
STYLE_BLOCK = re.compile(r"<style\b[^>]*>(.*?)</style>", re.I | re.S)
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
HTML_TYPE1_OPEN = re.compile(r"(?i)^ {0,3}<(script|pre|style|textarea)(?:\s|/?>|$)")
HTML_TYPE1_CLOSE = re.compile(r"(?i)</(script|pre|style|textarea)>")
HTML_UNTIL_OPEN = [
    (re.compile(r"^ {0,3}<!--"), "-->"),
    (re.compile(r"^ {0,3}<\?"), "?>"),
    (re.compile(r"^ {0,3}<!\[CDATA\["), "]]>"),
    (re.compile(r"^ {0,3}<![A-Za-z]"), ">"),
]
HTML_TYPE7_TAG = re.compile(r"^ {0,3}</?[a-zA-Z][a-zA-Z0-9-]*")


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


def recipe_body_usable(body: str) -> bool:
    """True when a recipe names core slots, signature slots, and exclusions."""
    return bool(RECIPE_SLOT.search(body) and RECIPE_SIG.search(body) and RECIPE_EXCLUDE.search(body))


def recipe_entry_ids(section: str) -> set[str]:
    found: set[str] = set()
    for raw in section.splitlines():
        line = raw.strip()
        listed = RECIPE_LIST.match(line)
        if listed:
            if recipe_body_usable(listed.group(2)):
                found.add(listed.group(1).lower())
            continue
        if line.startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            if cells and re.fullmatch(r"[a-z][a-z0-9_-]*", cells[0], re.I):
                rest = [cell for cell in cells[1:] if cell and not re.fullmatch(r":?-{3,}:?", cell)]
                if rest and recipe_body_usable(" ".join(rest)):
                    found.add(cells[0].lower())
            continue
        plain = RECIPE_PLAIN.match(line)
        if plain and recipe_body_usable(plain.group(2)):
            found.add(plain.group(1).lower())
    return found


def strip_html_comments(text: str) -> str:
    """Remove HTML comments. An unclosed comment hides through end of text."""
    pieces: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        start = text.find(HTML_COMMENT_OPEN, i)
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


class _CompletedTagCounter(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.starts = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        self.starts += 1

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.starts += 1


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
    return decode_css_escapes(CSS_COMMENT.sub("", style or ""))


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
    for _ in iter_css_declarations(style):
        return True
    return False


def winning_style_tokens(style: str) -> dict[str, str]:
    winning: dict[str, tuple[str, bool]] = {}
    for prop, value in iter_css_declarations(style):
        important = bool(CSS_IMPORTANT.search(value))
        raw = CSS_IMPORTANT.sub("", value).strip()
        token = raw.split()[0].lower() if raw else ""
        prev = winning.get(prop)
        if prev is not None and prev[1] and not important:
            continue
        winning[prop] = (token, important)
    return {prop: token for prop, (token, _imp) in winning.items()}


def _opacity_is_zero(token: str) -> bool:
    if not token:
        return False
    raw_token = token[:-1] if token.endswith("%") else token
    try:
        return float(raw_token) == 0
    except ValueError:
        return False


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

    def _type1_closed(self, raw: str, tag: str) -> bool:
        return bool(re.search(rf"(?i)</{re.escape(tag)}>", raw))

    def in_block(self, raw: str) -> bool:
        if self.type1:
            if self._type1_closed(raw, self.type1):
                self.type1 = None
            return True
        if self.until_close is not None:
            if self.until_close in raw:
                self.until_close = None
            return True
        if self.html_block:
            if not raw.strip():
                self.html_block = False
            return True
        type1_open = HTML_TYPE1_OPEN.match(raw)
        if type1_open:
            self.type1 = type1_open.group(1).lower()
            if self._type1_closed(raw, self.type1):
                self.type1 = None
            return True
        for rx, closer in HTML_UNTIL_OPEN:
            if rx.match(raw):
                if closer not in raw:
                    self.until_close = closer
                return True
        if HTML_BLOCK_OPEN.match(raw) or is_html_type7_line(raw):
            self.html_block = True
            return True
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
    return strip_html_comments(strip_html_blocks(unfenced_markdown(text)))


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


def extract_stylesheet_hide_rules(html: str) -> list[tuple[str, dict[str, str]]]:
    """Selectors from <style> whose declarations hide matching elements."""
    rules: list[tuple[str, dict[str, str]]] = []
    for block in STYLE_BLOCK.findall(html or ""):
        css = CSS_COMMENT.sub("", block)
        for match in re.finditer(r"([^{}]+)\{([^{}]+)\}", css):
            tokens = winning_style_tokens(match.group(2))
            hide: dict[str, str] = {}
            if tokens.get("display") == "none":
                hide["display"] = "none"
            if _opacity_is_zero(tokens.get("opacity", "")):
                hide["opacity"] = "0"
            vis = tokens.get("visibility")
            if vis in {"hidden", "collapse"}:
                hide["visibility"] = vis
            if not hide:
                continue
            for selector in match.group(1).split(","):
                sel = selector.strip()
                if sel:
                    rules.append((sel, hide))
    return rules


def css_selector_matches(selector: str, tag: str, attrs) -> bool:
    """Match the subject (rightmost compound) of a simple CSS selector."""
    parts = [part for part in CSS_COMBINATOR.split(selector.strip()) if part]
    if not parts:
        return False
    subject = parts[-1]
    if ":" in subject:
        subject = subject.split(":", 1)[0]
        if not subject:
            return False
    if subject == "*":
        return True
    ad = {name.lower(): (value or "") for name, value in attrs}
    i = 0
    n = len(subject)
    named = re.match(r"^[a-zA-Z][a-zA-Z0-9-]*", subject)
    if named:
        if named.group(0).lower() != tag:
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
            if ad.get("id") != subject[i + 1 : j]:
                return False
            i = j
        elif ch == ".":
            j = i + 1
            while j < n and subject[j] not in ".#[":
                j += 1
            if subject[i + 1 : j] not in ad.get("class", "").split():
                return False
            i = j
        elif ch == "[":
            end = subject.find("]", i)
            if end == -1:
                return False
            inner = subject[i + 1 : end].strip()
            if "=" in inner:
                aname, aval = inner.split("=", 1)
                if ad.get(aname.strip().lower()) != aval.strip().strip("\"'"):
                    return False
            elif inner.strip().lower() not in ad:
                return False
            i = end + 1
        else:
            return False
    return True


class PreviewMarkerCollector(HTMLParser):
    """Collect contiguous visible text and intended attributes; skip hidden subtrees."""

    def __init__(self, sheet_hides: list[tuple[str, dict[str, str]]] | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool, bool, bool, bool]] = []
        self.skip_depth = 0
        self.vis_hidden_stack: list[bool] = []
        self.text_buf: list[str] = []
        self.chunks: list[str] = []
        self.details_stack: list[dict[str, bool]] = []
        self.sheet_hides = sheet_hides or []

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

    def _sheet_hide(self, tag: str, attrs) -> tuple[bool, bool, str | None]:
        display_none = False
        opacity_zero = False
        vis: str | None = None
        for selector, hide in self.sheet_hides:
            if not css_selector_matches(selector, tag, attrs):
                continue
            if hide.get("display") == "none":
                display_none = True
            if "opacity" in hide:
                opacity_zero = True
            if hide.get("visibility") in {"hidden", "collapse"}:
                vis = hide["visibility"]
        return display_none, opacity_zero, vis

    def _open(self, tag: str, attrs) -> None:
        ltag = tag.lower()
        self._implied_close(ltag)
        self._close_nested_anchor(ltag)
        self._clear_table_stack(ltag)
        hidden = any(name.lower() == "hidden" for name, _ in attrs)
        style = next((value or "" for name, value in attrs if name.lower() == "style"), "")
        inline_tokens = winning_style_tokens(style)
        sheet_display_none, sheet_opacity_zero, sheet_vis = self._sheet_hide(ltag, attrs)
        if "display" in inline_tokens:
            sheet_display_none = inline_tokens["display"] == "none"
        if "opacity" in inline_tokens:
            sheet_opacity_zero = _opacity_is_zero(inline_tokens["opacity"])
        hard = hidden or sheet_display_none or sheet_opacity_zero
        if ltag == "input" and any(value.lower() == "hidden" for value in attr_values(attrs, "type")):
            hard = True
        if ltag == "dialog" and not any(name.lower() == "open" for name, _ in attrs):
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
        if "visibility" in inline_tokens:
            own_vis = inline_tokens["visibility"] if inline_tokens["visibility"] in {"hidden", "visible", "collapse"} else None
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
        self.stack.append((ltag, skip, hard, opened_closed_details, opened_summary, fallback))
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
            if self.stack[i][0] == ltag:
                if ltag in PREVIEW_BLOCK_BREAK and self.skip_depth == 0:
                    self._flush_text()
                for _, _was_skip, was_hard, opened_closed_details, opened_summary, was_fallback in reversed(self.stack[i:]):
                    if opened_summary and self.details_stack:
                        self.details_stack[-1]["in_summary"] = False
                    if opened_closed_details and self.details_stack:
                        self.details_stack.pop()
                    if was_hard or was_fallback:
                        self.skip_depth = max(0, self.skip_depth - 1)
                    if self.vis_hidden_stack:
                        self.vis_hidden_stack.pop()
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
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
    for match in COMPONENT_HEADING.finditer(md_text):
        if not _in_spans(match.start(), spans):
            continue
        region_start = match.end()
        nxt = None
        for nxt_match in re.finditer(r"(?m)^#{2,3} ", md_text[region_start:]):
            abs_pos = region_start + nxt_match.start()
            if _in_spans(abs_pos, spans):
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
        void = ltag in VOID_TAGS
        self._implied_close(ltag)
        self._close_nested_anchor(ltag)
        self._clear_table_stack(ltag)
        ad = {k.lower(): v for k, v in attrs}
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
            for size in FONT_SIZE.findall(stripped):
                if float(size) > 24:
                    self._add("ERROR", f"{self.label}: font-size {size}px 超过 24px")
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
            if self.stack[i][0] == ltag:
                matched = True
                for _, was_leaf in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                del self.stack[i:]
                break
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
        md_source = strip_html_comments(md_text)
        structure_md = visible_structure_markdown(md_text)
        for heading in REQUIRED_MD_HEADINGS:
            if not _has_heading_line(structure_md, heading):
                errors.append(f"THEME.md 缺少章节 {heading}")
        recipe = _md_section(structure_md, "## 文章类型配方")
        if recipe is not None:
            covered = recipe_entry_ids(recipe)
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

        for label, _kind, _ident, region_start, region_end in iter_component_regions(md_source):
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
