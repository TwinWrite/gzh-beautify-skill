#!/usr/bin/env python3
"""Validate WeChat-pasteable article HTML (inline styles, leaf spans, no banned CSS)."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from html.parser import HTMLParser

CJK = re.compile(r"[一-鿿㐀-䶿]")
HALF_PUNCT = re.compile(r"[,;!?:]|[\"']")
NUMERIC_SEP = re.compile(r"(?<=\d)[,:](?=\d)")
URL_OR_EMAIL = re.compile(
    r"(?i)(?:https?://|ftp://|mailto:)[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+|"
    r"www\.[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=%-]+|"
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
SCHEME_IGNORED = re.compile(r"[\x00-\x20\x7f]+")
CODE_STYLE = re.compile(r"monospace|courier|consolas|sf mono", re.I)
FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
PLACEHOLDER = re.compile(r"\{\{[a-zA-Z_][a-zA-Z0-9_]*\}\}")
EXEC_SCHEME = re.compile(
    r"^\s*(?:javascript|vbscript|livescript|mocha)\s*:|"
    r"^\s*data\s*:\s*(?:text\s*/\s*html|text\s*/\s*javascript|application\s*/\s*(?:javascript|ecmascript))",
    re.I,
)
EXEC_IN_STYLE = re.compile(r"javascript\s*:|expression\s*\(|-moz-binding", re.I)

SKIP_TAGS = {"head", "title", "style", "script"}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr", "param"}
HEADING_TAGS = frozenset({"h1", "h2", "h3", "h4", "h5", "h6"})


def html_tag_name(tag: str) -> str:
    ltag = (tag or "").lower()
    return "img" if ltag == "image" else ltag


def end_tag_matches(open_tag: str, end_tag: str) -> bool:
    if open_tag == end_tag:
        return True
    return open_tag in HEADING_TAGS and end_tag in HEADING_TAGS


DOCUMENT_TAGS = {"html", "head", "body"}
FORBIDDEN_TAGS = {
    "style": "<style> 会被过滤，样式必须内联",
    "script": "<script> 会被过滤",
    "div": "<div> 会被改写，请用 <section>",
    "link": "外链 <link> 会被过滤",
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
    "pre": "禁止 <pre>/<code>，代码块须逐行 <p>",
    "code": "禁止 <pre>/<code>，代码块须逐行 <p>",
    "meta": "禁止 <meta>，正文须为可粘贴片段",
    "base": "禁止 <base>，会改写相对链接",
    "plaintext": "禁止 <plaintext>，会破坏预览解析",
    "xmp": "禁止 <xmp>，会破坏预览解析",
    "template": "禁止 <template>，内容不会渲染",
    "select": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "option": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "optgroup": "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]",
    "dialog": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
    "details": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
    "noscript": "禁止 <dialog>/<details>/<noscript>，内容默认不渲染",
}
STYLE_FORBIDDEN = [
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "position fixed/absolute/sticky 不支持"),
    (re.compile(r"float\s*:", re.I), "float 不支持"),
    (re.compile(r"@media", re.I), "@media 不支持"),
    (re.compile(r"@keyframes", re.I), "@keyframes 不支持"),
    (re.compile(r"@import", re.I), "@import 不支持"),
    (re.compile(r"display\s*:\s*grid", re.I), "display:grid 不支持"),
    (re.compile(r"var\s*\(\s*--", re.I), "CSS 变量不支持"),
    (re.compile(r"white-space\s*:\s*pre", re.I), "white-space:pre 会造成大段空白"),
    (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(woff2?|ttf|otf|eot)", re.I), "外链字体不支持"),
]
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
BLOCK_NEED_STYLE = {
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


ACTIVE_DATA_TOKEN = re.compile(r"(?:html|svg|xml|javascript|ecmascript)", re.I)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_CSS_HEX = frozenset("0123456789abcdefABCDEF")
_CSS_ESCAPE_WS = frozenset(" \t\n\r\f")
RAW_UNSAFE = [
    (re.compile(r"<!\[", re.I), "禁止 CDATA / 不完整声明"),
    (re.compile(r"<script\b", re.I), "<script> 会被过滤"),
    (re.compile(r"<object\b", re.I), "出现禁止标签"),
    (re.compile(r"<embed\b", re.I), "出现禁止标签"),
    (re.compile(r"<iframe\b", re.I), "出现禁止标签"),
    (re.compile(r"<link\b", re.I), "外链 <link> 会被过滤"),
    (re.compile(r"<meta\b", re.I), "禁止 <meta>，正文须为可粘贴片段"),
    (re.compile(r"<base\b", re.I), "禁止 <base>，会改写相对链接"),
    (re.compile(r"<plaintext\b", re.I), "禁止 <plaintext>，会破坏预览解析"),
    (re.compile(r"<xmp\b", re.I), "禁止 <xmp>，会破坏预览解析"),
    (re.compile(r"<template\b", re.I), "禁止 <template>，内容不会渲染"),
    (re.compile(r"<select\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<option\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<optgroup\b", re.I), "禁止 <select>/<option>/<optgroup>，无法保留 span[leaf]"),
    (re.compile(r"<dialog\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"<details\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"<noscript\b", re.I), "禁止 <dialog>/<details>/<noscript>，内容默认不渲染"),
    (re.compile(r"</div\b", re.I), "<div> 会被改写，请用 <section>"),
]


def normalize_scheme_text(value: str) -> str:
    """Strip ASCII controls/spaces that URL processors ignore in schemes."""
    return SCHEME_IGNORED.sub("", value or "")


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
    text = normalize_scheme_text(value)
    if EXEC_SCHEME.search(text):
        return True
    lower = text.lower()
    if lower.startswith("data:"):
        return bool(ACTIVE_DATA_TOKEN.search(data_uri_media_type(lower)))
    return False


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


CSS_IMPORTANT = re.compile(r"!\s*important\s*$", re.I)
_CSS_ABS_PX = {
    "px": 1.0,
    "pt": 96.0 / 72.0,
    "pc": 16.0,
    "in": 96.0,
    "cm": 96.0 / 2.54,
    "mm": 96.0 / 25.4,
    "q": 96.0 / 101.6,
}
_CSS_DISPLAY_OK = frozenset({
    "none", "inline", "block", "inline-block", "flex", "inline-flex", "grid",
    "inline-grid", "flow-root", "contents", "list-item", "table", "inline-table",
    "table-row", "table-cell", "table-column", "table-column-group",
    "table-header-group", "table-footer-group", "table-row-group", "table-caption",
    "run-in", "-webkit-box", "-webkit-flex", "inherit", "initial", "unset",
    "revert", "revert-layer",
})
_CSS_VIS_OK = frozenset({
    "visible", "hidden", "collapse", "inherit", "initial", "unset", "revert", "revert-layer",
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
    "border-top-width", "border-width", "bottom", "box-shadow", "box-sizing",
    "caption-side", "caret-color", "clear", "clip-path", "color", "column-count",
    "column-gap", "columns", "contain", "content", "cursor", "direction", "display",
    "empty-cells", "filter", "flex", "flex-basis", "flex-direction", "flex-flow",
    "flex-grow", "flex-shrink", "flex-wrap", "float", "font", "font-family",
    "font-feature-settings", "font-kerning", "font-size", "font-stretch",
    "font-style", "font-variant", "font-weight", "gap", "grid", "grid-area",
    "grid-column", "grid-row", "grid-template", "grid-template-columns",
    "grid-template-rows", "height", "hyphens", "inset", "isolation",
    "justify-content", "justify-items", "justify-self", "left", "letter-spacing",
    "line-break", "line-height", "list-style", "list-style-image",
    "list-style-position", "list-style-type", "margin", "margin-bottom",
    "margin-left", "margin-right", "margin-top", "mask", "max-height", "max-width",
    "min-height", "min-width", "mix-blend-mode", "object-fit", "object-position",
    "opacity", "order", "outline", "outline-color", "outline-offset", "outline-style",
    "outline-width", "overflow", "overflow-wrap", "overflow-x", "overflow-y",
    "padding", "padding-bottom", "padding-left", "padding-right", "padding-top",
    "place-content", "place-items", "place-self", "pointer-events", "position",
    "quotes", "resize", "right", "row-gap", "table-layout", "text-align",
    "text-align-last", "text-decoration", "text-decoration-color",
    "text-decoration-line", "text-decoration-style", "text-emphasis", "text-indent",
    "text-overflow", "text-shadow", "text-transform", "text-underline-offset",
    "top", "transform", "transform-origin", "transition", "unicode-bidi",
    "user-select", "vertical-align", "visibility", "white-space", "width",
    "will-change", "word-break", "word-spacing", "writing-mode", "z-index",
})


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


def css_numeric_opacity(token: str) -> float | None:
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


def has_css_declaration(style: str) -> bool:
    """True when style has at least one supported property with a valid value."""
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


def css_font_size_value_ok(raw: str) -> bool:
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


def attr_values(attrs, name: str) -> list[str]:
    lname = name.lower()
    return [(value or "") for key, value in attrs if key.lower() == lname]


def prose_without_urls(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(0)
        trimmed = raw.rstrip(".,;:!?)]}\"'" )
        return " " + raw[len(trimmed) :]

    return URL_OR_EMAIL.sub(repl, text)


def prose_for_punct(text: str) -> str:
    """Drop URLs and digit-flanked numeric separators before half-width checks."""
    return NUMERIC_SEP.sub(" ", prose_without_urls(text))


class ArticleChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.leaf_depth = 0
        self.code_depth = 0
        self.span_leaf_count = 0
        self.unwrapped: list[tuple[str, str]] = []
        self.half_punct: list[str] = []
        self.leaf_has_block = False
        self.top_level: list[tuple[str, dict[str, str | None]]] = []
        self.has_document_wrapper = False
        self.root_text: list[str] = []
        self.tag_hits: Counter[str] = Counter()
        self.class_count = 0
        self.id_count = 0
        self.event_attrs: list[str] = []
        self.exec_urls: list[str] = []
        self.css_hits: list[str] = []
        self.font_size_hits: list[str] = []
        self.unstyled_blocks: Counter[str] = Counter()
        self.style_count = 0
        self.styled_root = False
        self.dup_style_count = 0
        self.img_bad_style = 0
        self.prose_buf: list[str] = []

    def _flush_prose(self) -> None:
        joined = "".join(self.prose_buf)
        self.prose_buf.clear()
        if not joined or self.code_depth:
            return
        if CJK.search(joined) and HALF_PUNCT.search(prose_for_punct(joined)):
            snippet = joined.strip()[:24] + ("…" if len(joined.strip()) > 24 else "")
            self.half_punct.append(snippet)

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
        if ltag in LEAF_BLOCK_TAGS:
            self._flush_prose()
        ad = {k.lower(): v for k, v in attrs}
        styles = attr_values(attrs, "style")
        at_root = not self.stack
        if at_root:
            self.top_level.append((ltag, ad))

        if ltag in DOCUMENT_TAGS:
            self.has_document_wrapper = True
        if ltag in FORBIDDEN_TAGS:
            self.tag_hits[ltag] += 1

        if len(styles) > 1:
            self.dup_style_count += 1
        effective_style = styles[0] if styles else ""
        if has_css_declaration(effective_style):
            self.style_count += 1
        elif ltag in BLOCK_NEED_STYLE:
            self.unstyled_blocks[ltag] += 1
        if at_root and ltag == "section":
            self.styled_root = has_root_layout(effective_style)
        if ltag == "img" and not has_responsive_image_style(effective_style):
            self.img_bad_style += 1

        if "class" in ad:
            self.class_count += 1
        if "id" in ad:
            self.id_count += 1

        for name, value in attrs:
            lname = name.lower()
            if lname.startswith("on") and len(lname) > 2:
                self.event_attrs.append(lname)
            if lname in URL_ATTRS and is_executable_url(value or ""):
                self.exec_urls.append(lname)
        for style in styles:
            stripped = normalize_style(style)
            normalized = normalize_scheme_text(stripped)
            if stripped and (EXEC_IN_STYLE.search(stripped) or EXEC_IN_STYLE.search(normalized)):
                self.exec_urls.append("style")
            for rx, msg in STYLE_FORBIDDEN:
                if rx.search(stripped):
                    self.css_hits.append(msg)
            self.font_size_hits.extend(font_size_limit_hits(style))

        is_leaf = ltag == "span" and "leaf" in ad
        is_code = bool(CODE_STYLE.search(normalize_style(effective_style)))
        if is_leaf:
            self.span_leaf_count += 1
            self.leaf_depth += 1
        if is_code and not void:
            self._flush_prose()
            self.code_depth += 1
        if self.leaf_depth and ltag in LEAF_BLOCK_TAGS:
            self.leaf_has_block = True
        if not void:
            self.stack.append((ltag, is_leaf, is_code))

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        matched = False
        for i in range(len(self.stack) - 1, -1, -1):
            if end_tag_matches(self.stack[i][0], ltag):
                matched = True
                if ltag in LEAF_BLOCK_TAGS:
                    self._flush_prose()
                for _, was_leaf, was_code in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                    if was_code:
                        self.code_depth -= 1
                del self.stack[i:]
                break
        if matched:
            return
        if ltag == "p":
            # HTML tree builder inserts an empty <p> for a stray </p>, then closes it.
            self._open("p", [], void=False)
            self.handle_endtag("p")
            return
        if ltag == "br":
            # HTML tree builder reprocesses stray </br> as a <br> start tag.
            self._open("br", [], void=True)
            return
        if ltag in FORBIDDEN_TAGS:
            self.tag_hits[ltag] += 1

    def handle_data(self, data: str) -> None:
        if not self.stack:
            text = data.lstrip("\ufeff").strip()
            if text:
                self.root_text.append(text[:24])
            return
        if any(t in SKIP_TAGS for t, _, _ in self.stack):
            return
        if self.code_depth == 0:
            self.prose_buf.append(data)
        text = data.strip()
        if not text or not CJK.search(text):
            return
        if self.leaf_depth == 0:
            parent = self.stack[-1][0] if self.stack else "(root)"
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.unwrapped.append((snippet, parent))


def _count_msg(template: str, n: int) -> str:
    return f"{template}（命中 {n} 处）"


def scan_raw_markup(html: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for rx, msg in RAW_UNSAFE:
        if rx.search(html) and msg not in seen:
            seen.add(msg)
            found.append(msg)
    return found


def validate(html: str) -> tuple[list[str], list[str], int]:
    html = html.lstrip("\ufeff")
    errors: list[str] = []
    warnings: list[str] = []

    leftover = PLACEHOLDER.findall(html)
    if leftover:
        warnings.append(f"仍有 {len(leftover)} 处 {{{{占位符}}}} 未替换，例 {leftover[0]}")

    errors.extend(scan_raw_markup(html))

    checker = ArticleChecker()
    try:
        checker.feed(html)
        checker.close()
    except Exception as exc:  # noqa: BLE001 — parser errors should not crash lint
        warnings.append(f"HTML 解析中断: {exc}")
    checker._flush_prose()

    emitted_tag_msgs: set[str] = set()
    for tag, n in checker.tag_hits.items():
        msg = FORBIDDEN_TAGS[tag]
        if msg in emitted_tag_msgs:
            continue
        emitted_tag_msgs.add(msg)
        total = n
        if tag in {"pre", "code"}:
            total = checker.tag_hits["pre"] + checker.tag_hits["code"]
        errors.append(_count_msg(msg, total))
    if checker.class_count:
        errors.append(_count_msg("class 无样式表可挂，交付正文禁止", checker.class_count))
    if checker.id_count:
        errors.append(_count_msg("id 会被剥离", checker.id_count))
    if checker.event_attrs:
        sample = "、".join(sorted(set(checker.event_attrs))[:6])
        errors.append(_count_msg(f"禁止事件属性（{sample}）", len(checker.event_attrs)))
    if checker.dup_style_count:
        errors.append(_count_msg("禁止重复 style 属性", checker.dup_style_count))
    if checker.exec_urls:
        errors.append(_count_msg("禁止 javascript:/vbscript:/data:html 等可执行 URL", len(checker.exec_urls)))
    for msg, n in Counter(checker.css_hits).items():
        errors.append(_count_msg(msg, n))
    if checker.font_size_hits:
        errors.append(f"font-size {checker.font_size_hits[0]} 超过 24px")
    if checker.img_bad_style:
        errors.append(
            _count_msg(
                "<img> 须含 max-width:100%;height:auto;display:block;margin:0 auto",
                checker.img_bad_style,
            )
        )

    if checker.has_document_wrapper:
        errors.append("正文不要包 <html>/<head>/<body>，须为可粘贴片段")
    if checker.root_text:
        errors.append("根节点旁出现裸文本，正文须是单一 <section>")
    if len(checker.top_level) != 1 or checker.top_level[0][0] != "section":
        kinds = ", ".join(t for t, _ in checker.top_level[:6]) or "(空)"
        errors.append(f"正文必须恰好一个顶层 <section> 根节点，当前: {kinds}")
    elif not checker.styled_root:
        errors.append("根 section 须含 max-width:677px 与水平 margin:0 auto 的 style")

    if checker.style_count == 0:
        errors.append("全文没有 inline style，平台只会保留内联样式")
    elif checker.unstyled_blocks:
        sample = "、".join(f"<{t}>×{n}" for t, n in checker.unstyled_blocks.most_common(5))
        errors.append(f"{sum(checker.unstyled_blocks.values())} 个标签缺少 style（{sample}）")

    if checker.leaf_has_block:
        errors.append("span[leaf] 内出现块级标签")

    has_cjk = bool(CJK.search(html))
    if has_cjk and checker.span_leaf_count == 0:
        errors.append("全文没有 span[leaf] 包裹，粘贴后样式会丢失")
    elif checker.unwrapped:
        sample = "；".join(f"「{s}」(在 <{p}> 内)" for s, p in checker.unwrapped[:5])
        errors.append(f"{len(checker.unwrapped)} 处中文未被 span[leaf] 包裹。例：{sample}")

    if checker.half_punct:
        sample = "；".join(f"「{s}」" for s in checker.half_punct[:5])
        warnings.append(
            f"{len(checker.half_punct)} 处正文疑似半角标点或直引号，应改全角（代码块不计）。例：{sample}"
        )

    return errors, warnings, checker.span_leaf_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验可粘贴进公众号的正文 HTML")
    parser.add_argument("file", nargs="?", help="HTML 文件路径")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取")
    parser.add_argument("--strict", action="store_true", help="把 WARNING 也当作失败")
    args = parser.parse_args(argv)

    if args.stdin or not args.file:
        html = sys.stdin.read()
        name = "<stdin>"
    else:
        path = args.file
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            html = handle.read()
        name = path

    errors, warnings, leaf_n = validate(html)
    print(f"公众号正文校验: {name}")
    print(f"  span[leaf] ×{leaf_n}")
    if errors:
        print(f"\nERROR ×{len(errors)}")
        for item in errors:
            print(f"  - {item}")
    if warnings:
        print(f"\nWARNING ×{len(warnings)}")
        for item in warnings:
            print(f"  - {item}")
    if not errors and not warnings:
        print("\n通过")
    elif not errors:
        print("\n无 ERROR" + ("；--strict 下 WARNING 仍算失败" if args.strict else ""))

    failed = bool(errors) or (args.strict and bool(warnings))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
