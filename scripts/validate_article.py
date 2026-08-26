#!/usr/bin/env python3
"""Validate WeChat-pasteable article HTML (inline styles, leaf spans, no banned CSS)."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser

FORBIDDEN = [
    (re.compile(r"<style[\s>]", re.I), "ERROR", "<style> 会被过滤，样式必须内联"),
    (re.compile(r"<script[\s>]", re.I), "ERROR", "<script> 会被过滤"),
    (re.compile(r"</?div[\s>]", re.I), "ERROR", "<div> 会被改写，请用 <section>"),
    (re.compile(r"<link[\s>]", re.I), "ERROR", "外链 <link> 会被过滤"),
    (re.compile(r"\sclass\s*=", re.I), "ERROR", "class 无样式表可挂，交付正文禁止"),
    (re.compile(r"\sid\s*=", re.I), "ERROR", "id 会被剥离"),
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "ERROR", "position fixed/absolute/sticky 不支持"),
    (re.compile(r"float\s*:", re.I), "ERROR", "float 不支持"),
    (re.compile(r"@media", re.I), "ERROR", "@media 不支持"),
    (re.compile(r"@keyframes", re.I), "ERROR", "@keyframes 不支持"),
    (re.compile(r"@import", re.I), "ERROR", "@import 不支持"),
    (re.compile(r"display\s*:\s*grid", re.I), "ERROR", "display:grid 不支持"),
    (re.compile(r"var\s*\(\s*--", re.I), "ERROR", "CSS 变量不支持"),
    (re.compile(r"white-space\s*:\s*pre", re.I), "ERROR", "white-space:pre 会造成大段空白"),
    (re.compile(r"</?(svg|canvas|video|audio|iframe|form|button|input)\b", re.I), "ERROR", "出现禁止标签"),
    (re.compile(r"url\s*\(\s*['\"]?https?://[^)]*\.(woff2?|ttf|otf|eot)", re.I), "ERROR", "外链字体不支持"),
]

FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
CJK = re.compile(r"[一-鿿㐀-䶿]")
HALF_PUNCT = re.compile(r"[一-鿿㐀-䶿][,;!?]")
ASCII_QUOTE = re.compile(r"[\"']")
CODE_STYLE = re.compile(r"monospace|courier|consolas|sf mono", re.I)
SKIP_TAGS = {"head", "title", "style", "script"}
PLACEHOLDER = re.compile(r"\{\{[a-z0-9_]+\}\}", re.I)


class LeafChecker(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.leaf_depth = 0
        self.code_depth = 0
        self.span_leaf_count = 0
        self.unwrapped: list[tuple[str, str]] = []
        self.half_punct: list[str] = []
        self.leaf_has_block = False

    def handle_starttag(self, tag: str, attrs) -> None:
        ad = dict(attrs)
        is_leaf = tag == "span" and "leaf" in ad
        is_code = bool(CODE_STYLE.search(ad.get("style", "") or ""))
        if is_leaf:
            self.span_leaf_count += 1
            self.leaf_depth += 1
        if is_code:
            self.code_depth += 1
        if self.leaf_depth and tag in {"section", "div", "p", "h1", "h2", "h3", "table", "ul", "ol"}:
            self.leaf_has_block = True
        self.stack.append((tag, is_leaf, is_code))

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for _, was_leaf, was_code in self.stack[i:]:
                    if was_leaf:
                        self.leaf_depth -= 1
                    if was_code:
                        self.code_depth -= 1
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text or not CJK.search(text):
            return
        if any(t in SKIP_TAGS for t, _, _ in self.stack):
            return
        if self.leaf_depth == 0:
            parent = self.stack[-1][0] if self.stack else "(root)"
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.unwrapped.append((snippet, parent))
        if self.code_depth == 0 and (HALF_PUNCT.search(text) or ASCII_QUOTE.search(text)):
            snippet = text[:24] + ("…" if len(text) > 24 else "")
            self.half_punct.append(snippet)


def validate(html: str) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []

    for rx, _level, msg in FORBIDDEN:
        hits = len(rx.findall(html))
        if hits:
            errors.append(f"{msg}（命中 {hits} 处）")

    for size in FONT_SIZE.findall(html):
        if float(size) > 24:
            errors.append(f"font-size {size}px 超过 24px")
            break

    leftover = PLACEHOLDER.findall(html)
    if leftover:
        warnings.append(f"仍有 {len(leftover)} 处 {{{{占位符}}}} 未替换，例 {leftover[0]}")

    checker = LeafChecker()
    try:
        checker.feed(html)
    except Exception as exc:  # noqa: BLE001 — parser errors should not crash lint
        warnings.append(f"HTML 解析中断: {exc}")

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
        with open(path, encoding="utf-8", errors="replace") as handle:
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
