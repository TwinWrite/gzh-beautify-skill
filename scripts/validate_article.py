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
URL_OR_EMAIL = re.compile(
    r"(?i)(?:https?://|ftp://|mailto:)[^\s<>\"']+|"
    r"www\.[^\s<>\"']+|"
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
SCHEME_IGNORED = re.compile(r"[\x00-\x20\x7f]+")
CODE_STYLE = re.compile(r"monospace|courier|consolas|sf mono", re.I)
FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
PLACEHOLDER = re.compile(r"\{\{[a-z0-9_]+\}\}", re.I)
EXEC_SCHEME = re.compile(
    r"^\s*(?:javascript|vbscript|livescript|mocha)\s*:|"
    r"^\s*data\s*:\s*(?:text\s*/\s*html|text\s*/\s*javascript|application\s*/\s*(?:javascript|ecmascript))",
    re.I,
)
EXEC_IN_STYLE = re.compile(r"javascript\s*:|expression\s*\(|-moz-binding", re.I)

SKIP_TAGS = {"head", "title", "style", "script"}
VOID_TAGS = {"img", "br", "hr", "input", "meta", "link", "area", "base", "col", "embed", "source", "track", "wbr"}
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
BLOCK_NEED_STYLE = {"section", "p", "h1", "h2", "h3", "ul", "ol", "table", "figure", "blockquote", "hr"}
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
RAW_UNSAFE = [
    (re.compile(r"<!\[", re.I), "禁止 CDATA / 不完整声明"),
    (re.compile(r"<script\b", re.I), "<script> 会被过滤"),
    (re.compile(r"<object\b", re.I), "出现禁止标签"),
    (re.compile(r"<embed\b", re.I), "出现禁止标签"),
    (re.compile(r"<iframe\b", re.I), "出现禁止标签"),
    (re.compile(r"<meta\b", re.I), "禁止 <meta>，正文须为可粘贴片段"),
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


def has_css_declaration(style: str) -> bool:
    """True when style has at least one property with a non-empty value."""
    if not style:
        return False
    stripped = CSS_COMMENT.sub("", style)
    for part in stripped.split(";"):
        piece = part.strip()
        if ":" not in piece:
            continue
        prop, value = piece.split(":", 1)
        if prop.strip() and value.strip():
            return True
    return False


def attr_values(attrs, name: str) -> list[str]:
    lname = name.lower()
    return [(value or "") for key, value in attrs if key.lower() == lname]


def prose_without_urls(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        raw = match.group(0)
        trimmed = raw.rstrip(".,;:!?)]}\"'" )
        return " " + raw[len(trimmed) :]

    return URL_OR_EMAIL.sub(repl, text)


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

    def handle_startendtag(self, tag: str, attrs) -> None:
        self._open(tag, attrs, void=tag.lower() in VOID_TAGS)

    def handle_starttag(self, tag: str, attrs) -> None:
        self._open(tag, attrs, void=tag.lower() in VOID_TAGS)

    def _open(self, tag: str, attrs, *, void: bool) -> None:
        ltag = tag.lower()
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
            if at_root and ltag == "section":
                self.styled_root = True
        elif ltag in BLOCK_NEED_STYLE:
            self.unstyled_blocks[ltag] += 1

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
            normalized = normalize_scheme_text(style)
            if style and (EXEC_IN_STYLE.search(style) or EXEC_IN_STYLE.search(normalized)):
                self.exec_urls.append("style")
            for rx, msg in STYLE_FORBIDDEN:
                if rx.search(style):
                    self.css_hits.append(msg)
            for size in FONT_SIZE.findall(style):
                if float(size) > 24:
                    self.font_size_hits.append(size)

        is_leaf = ltag == "span" and "leaf" in ad
        is_code = bool(CODE_STYLE.search(effective_style))
        if is_leaf:
            self.span_leaf_count += 1
            self.leaf_depth += 1
        if is_code:
            self.code_depth += 1
        if self.leaf_depth and ltag in {"section", "div", "p", "h1", "h2", "h3", "table", "ul", "ol"}:
            self.leaf_has_block = True
        if not void:
            self.stack.append((ltag, is_leaf, is_code))

    def handle_endtag(self, tag: str) -> None:
        ltag = tag.lower()
        matched = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == ltag:
                matched = True
                for _, was_leaf, was_code in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                    if was_code:
                        self.code_depth -= 1
                del self.stack[i:]
                break
        if not matched and ltag in FORBIDDEN_TAGS:
            self.tag_hits[ltag] += 1

    def handle_data(self, data: str) -> None:
        if not self.stack:
            text = data.lstrip("\ufeff").strip()
            if text:
                self.root_text.append(text[:24])
            return
        text = data.strip()
        if not text or not CJK.search(text):
            return
        if any(t in SKIP_TAGS for t, _, _ in self.stack):
            return
        if self.leaf_depth == 0:
            parent = self.stack[-1][0] if self.stack else "(root)"
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.unwrapped.append((snippet, parent))
        if self.code_depth == 0 and HALF_PUNCT.search(prose_without_urls(text)):
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.half_punct.append(snippet)


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
        errors.append(f"font-size {checker.font_size_hits[0]}px 超过 24px")

    if checker.has_document_wrapper:
        errors.append("正文不要包 <html>/<head>/<body>，须为可粘贴片段")
    if checker.root_text:
        errors.append("根节点旁出现裸文本，正文须是单一 <section>")
    if len(checker.top_level) != 1 or checker.top_level[0][0] != "section":
        kinds = ", ".join(t for t, _ in checker.top_level[:6]) or "(空)"
        errors.append(f"正文必须恰好一个顶层 <section> 根节点，当前: {kinds}")
    elif not checker.styled_root:
        errors.append("根 section 缺少 style")

    if checker.style_count == 0:
        errors.append("全文没有 inline style，平台只会保留内联样式")
    elif checker.unstyled_blocks:
        sample = "、".join(f"<{t}>×{n}" for t, n in checker.unstyled_blocks.most_common(5))
        errors.append(f"{sum(checker.unstyled_blocks.values())} 个块级标签缺少 style（{sample}）")

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
