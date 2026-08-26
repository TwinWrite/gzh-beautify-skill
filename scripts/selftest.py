#!/usr/bin/env python3
"""Repo self-test for lint/validate/wrap. No network."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import lint_theme  # noqa: E402
import validate_article  # noqa: E402
import wrap_preview  # noqa: E402

REQUIRED = lint_theme.REQUIRED_SLOTS


def _slot_html(slot: str) -> str:
    if slot == "root":
        return (
            '<section style="max-width:677px;margin:0 auto;background:#FFFFFF;color:#1F2937;">\n'
            "  <!-- children -->\n"
            "</section>\n"
        )
    if slot == "divider":
        return (
            '<section style="height:1px;background:#E5E7EB;margin:24px 0;">'
            '<span leaf=""><br></span></section>\n'
        )
    if slot == "media_ph":
        return (
            '<section style="margin:0 0 24px;padding:24px;border:1.5px dashed #D1D5DB;'
            'border-radius:12px;background:#FAFAF8;text-align:center;">'
            '<p style="margin:0;font-size:14px;color:#6B7280;"><span leaf="">{{body}}</span></p>'
            "</section>\n"
        )
    if slot.startswith("code_"):
        return (
            '<section style="margin:0 0 20px;background:#0F172A;border-radius:8px;">'
            '<p style="margin:0;padding:12px;font-family:Consolas,Monaco,monospace;'
            'font-size:13px;color:#E2E8F0;"><span leaf="">{{line}}</span></p></section>\n'
        )
    return (
        '<p style="margin:0 0 12px;font-size:16px;color:#1F2937;">'
        '<span leaf="">{{' + slot + "}}</span></p>\n"
    )


def write_mini_theme(path: Path, *, omit_footer: bool = False, pale_ink: bool = False) -> None:
    path.mkdir(parents=True, exist_ok=True)
    slots = [s for s in REQUIRED if not (omit_footer and s == "footer")]
    sigs = [f"sig-demo-{i}" for i in range(1, 9)]
    ink = "#F3F4F6" if pale_ink else "#1F2937"
    data = {
        "id": path.name,
        "name": "试色",
        "version": 1,
        "description": "自测用主题包，不是可选用的成品主题。",
        "structure_model": {
            "voice": "explainer",
            "density": "balanced",
            "heading": "numbered-chapter",
            "surface": "hairline",
            "rhythm": "documentary",
        },
        "tokens": {
            "color": {
                "page": "#FFFFFF",
                "ink": ink,
                "ink_muted": "#4B5563",
                "brand": "#1D4E89",
                "brand_soft": "#E8F0FA",
                "brand_ink": "#163A66",
                "accent": "#C2410C",
                "rule": "#E5E7EB",
                "underline": "#BFDBFE",
            },
            "type": {
                "stack": "sans",
                "body_size": "15px",
                "body_line_height": "1.8",
                "max_title_size": "22px",
            },
            "shape": {"radius": "8px", "shadow": "none"},
            "layout": {"max_width": "677px", "gutter": "20px"},
        },
        "underline_css": "border-bottom:2px solid #BFDBFE;font-weight:600;",
        "tags": {
            "craft": ["细线", "编号章节"],
            "mood": ["克制", "清晰"],
            "scenes": ["教程", "说明"],
        },
        "slots": slots if omit_footer else list(REQUIRED),
        "signature_slots": sigs,
        "files": {"library": "THEME.md", "preview": "preview.html"},
    }
    (path / "theme.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# 试色\n", "## 结构模型\n\nexplainer / balanced\n"]
    md.append("## 设计变量\n\n见 theme.json\n")
    md.append("## 必选槽\n")
    for slot in REQUIRED:
        if omit_footer and slot == "footer":
            continue
        md.append(f"### slot:{slot}\n\n```html\n{_slot_html(slot)}```\n")
    md.append("## 签名槽\n")
    for sig in sigs:
        md.append(f"### sig:{sig}\n\n```html\n{_slot_html(sig)}```\n")
    md.append("## 文章骨架\n\n1. root\n2. hero\n3. toc\n4. h2 循环\n5. footer\n")
    md.append("## 文章类型配方\n\n")
    for kind in lint_theme.ARTICLE_TYPES:
        md.append(f"- `{kind}`: hero + h2 + paragraph\n")
    md.append("\n## Markdown 映射\n\n| Markdown | 槽 |\n|---|---|\n| `#` | hero |\n")
    (path / "THEME.md").write_text("".join(md), encoding="utf-8")

    preview_bits = ["<!DOCTYPE html><html><head><meta charset='utf-8'><title>preview</title></head><body>"]
    for slot in REQUIRED:
        preview_bits.append(f"<p>slot:{slot}</p>")
    for sig in sigs:
        preview_bits.append(f"<p>sig:{sig}</p>")
    preview_bits.append("</body></html>")
    (path / "preview.html").write_text("".join(preview_bits), encoding="utf-8")


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True)


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


def main() -> int:
    schema = lint_theme.load_schema(ROOT)

    errors, warnings, leaf_n = validate_article.validate(
        (SCRIPTS / "testdata" / "valid_article.html").read_text(encoding="utf-8")
    )
    assert_true(not errors, f"valid_article 不应有 ERROR: {errors}")
    assert_true(leaf_n >= 1, "valid_article 应有 leaf")

    bad_html = (SCRIPTS / "testdata" / "invalid_article.html").read_text(encoding="utf-8")
    errors, warnings, _ = validate_article.validate(bad_html)
    assert_true(any("div" in e.lower() or "<div>" in e for e in errors), f"invalid 应抓到 div: {errors}")
    assert_true(any("leaf" in e.lower() or "包裹" in e for e in errors), f"invalid 应抓到未包裹中文: {errors}")

    ok = run_cli([sys.executable, str(SCRIPTS / "validate_article.py"), str(SCRIPTS / "testdata" / "valid_article.html")])
    assert_true(ok.returncode == 0, f"validate valid 退出码 {ok.returncode}\n{ok.stdout}{ok.stderr}")
    bad = run_cli([sys.executable, str(SCRIPTS / "validate_article.py"), str(SCRIPTS / "testdata" / "invalid_article.html")])
    assert_true(bad.returncode == 1, "validate invalid 应失败")

    with tempfile.TemporaryDirectory() as tmp:
        preview_out = Path(tmp) / "out.html"
        wrap_preview.wrap(SCRIPTS / "testdata" / "valid_article.html", preview_out)
        text = preview_out.read_text(encoding="utf-8")
        assert_true("gzhb-copy" in text, "预览页应有复制按钮")
        article_start = text.find('id="gzhb-article"')
        article_html = text[article_start:]
        inner = article_html.split(">", 1)[1]
        # toolbar markup must not sit inside the copied node as source siblings of the article
        copied = inner.rsplit("</div>", 1)[0]
        assert_true("gzhb-bar" not in copied, "工具条不得进入被复制正文")
        assert_true("span leaf" in copied, "正文应保留 leaf")

        empty = Path(tmp) / "themes"
        empty.mkdir()
        empty_run = run_cli([sys.executable, str(SCRIPTS / "lint_theme.py"), str(empty)])
        assert_true(empty_run.returncode == 0, f"空 themes 应通过: {empty_run.stdout}")

        good_dir = Path(tmp) / "trial-pack"
        write_mini_theme(good_dir)
        g_err, g_warn = lint_theme.lint_theme(good_dir, schema)
        assert_true(not g_err, f"迷你主题不应有 ERROR: {g_err}")

        pale = Path(tmp) / "pale-pack"
        write_mini_theme(pale, pale_ink=True)
        p_err, _ = lint_theme.lint_theme(pale, schema)
        assert_true(any("对比度" in e for e in p_err), f"浅字应报对比度: {p_err}")

        missing = Path(tmp) / "missing-pack"
        write_mini_theme(missing, omit_footer=True)
        m_err, _ = lint_theme.lint_theme(missing, schema)
        assert_true(any("footer" in e for e in m_err), f"缺 footer 应失败: {m_err}")

        lint_ok = run_cli([sys.executable, str(SCRIPTS / "lint_theme.py"), str(good_dir)])
        assert_true(lint_ok.returncode == 0, f"lint mini 应通过\n{lint_ok.stdout}{lint_ok.stderr}")

    print("selftest: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
