#!/usr/bin/env python3
"""Wrap a clean article section in the local preview shell (copy button lives outside the article)."""

from __future__ import annotations

import sys
from pathlib import Path


def wrap(src: Path, dest: Path | None = None) -> Path:
    if not src.is_file():
        raise FileNotFoundError(src)
    skill_root = Path(__file__).resolve().parent.parent
    shell = skill_root / "assets" / "preview-shell.html"
    template = shell.read_text(encoding="utf-8")
    article = src.read_text(encoding="utf-8").strip()
    title = src.stem
    html = template.replace("{{TITLE}}", title).replace("{{ARTICLE}}", article)
    if dest is None:
        dest = src.with_name(src.stem + "_预览.html")
    dest.write_text(html, encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("用法: wrap_preview.py <正文.html> [预览.html]")
        return 1
    src = Path(argv[0])
    dest = Path(argv[1]) if len(argv) > 1 else None
    try:
        out = wrap(src, dest)
    except FileNotFoundError:
        print(f"找不到文件: {src}")
        return 1
    print(f"已生成预览: {out}")
    print("用浏览器打开，点「复制到公众号」，再到编辑器粘贴。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
