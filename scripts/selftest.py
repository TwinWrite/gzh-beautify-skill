#!/usr/bin/env python3
"""Repo self-test for lint/validate/wrap. No network."""

from __future__ import annotations

import json
import re
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


def assert_has(items: list[str], needle: str, msg: str) -> None:
    assert_true(any(needle in item for item in items), f"{msg}: {items}")


def styled_root(inner: str) -> str:
    return (
        '<section style="max-width:677px;margin:0 auto;background:#FFFFFF;color:#1F2937;">'
        f"{inner}"
        "</section>"
    )


def body_p(text: str, *, code: bool = False) -> str:
    font = "font-family:Consolas,Monaco,monospace;font-size:13px;" if code else "font-size:16px;line-height:1.8;"
    return f'<p style="{font}margin:0 0 16px;color:#1F2937;"><span leaf="">{text}</span></p>'


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

    grid_in_code = styled_root(body_p("display:grid 示例", code=True))
    g_err, g_warn, _ = validate_article.validate(grid_in_code)
    assert_true(not any("grid" in e.lower() for e in g_err), f"代码里的 display:grid 不应报错: {g_err}")

    grid_in_style = (
        '<section style="display:grid;max-width:677px;margin:0 auto;">'
        f"{body_p('正文。')}</section>"
    )
    gs_err, _, _ = validate_article.validate(grid_in_style)
    assert_has(gs_err, "grid", "style 里的 display:grid 应报错")

    bare = "<section><p><span leaf=\"\">正文。</span></p></section>"
    b_err, _, _ = validate_article.validate(bare)
    assert_true(any("style" in e.lower() for e in b_err), f"无 inline style 应失败: {b_err}")

    mixed = styled_root(body_p("使用 Python, 然后继续。") + body_p("版本 v2.0: 已发布。"))
    _, m_warn, _ = validate_article.validate(mixed)
    assert_true(any("半角" in w for w in m_warn), f"拉丁字母后的半角标点应警告: {m_warn}")

    pre = styled_root("<pre style=\"font-size:13px;\"><code>print(1)</code></pre>")
    p_err, _, _ = validate_article.validate(pre)
    assert_true(any("pre" in e.lower() or "code" in e.lower() for e in p_err), f"<pre><code> 应失败: {p_err}")

    xss = styled_root(f"{body_p('正文。')}<img src=\"missing\" onerror=\"alert(1)\">")
    x_err, _, _ = validate_article.validate(xss)
    assert_true(any("事件" in e or "onerror" in e.lower() for e in x_err), f"onerror 应失败: {x_err}")

    js_link = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;"><a href="javascript:alert(1)"><span leaf="">点击。</span></a></p>'
    )
    j_err, _, _ = validate_article.validate(js_link)
    assert_true(any("javascript" in e.lower() or "可执行" in e for e in j_err), f"javascript: 应失败: {j_err}")

    tabbed_js = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;">'
        '<a href="java&#x09;script:alert(1)"><span leaf="">点击。</span></a></p>'
    )
    tj_err, _, _ = validate_article.validate(tabbed_js)
    assert_true(any("可执行" in e or "javascript" in e.lower() for e in tj_err), f"java\\tscript: 应失败: {tj_err}")

    dup_style = (
        '<section style="position:absolute;max-width:677px" style="max-width:677px;margin:0 auto">'
        f"{body_p('正文。')}</section>"
    )
    ds_err, _, _ = validate_article.validate(dup_style)
    assert_true(any("position" in e.lower() or "absolute" in e.lower() for e in ds_err), f"重复 style 应抓到 position: {ds_err}")

    url_prose = styled_root(body_p("访问 https://example.com 获取资料。"))
    _, url_warn, _ = validate_article.validate(url_prose)
    assert_true(not any("半角" in w for w in url_warn), f"正文 URL 不应报半角标点: {url_warn}")

    empty_first_style = (
        '<section style="" style="max-width:677px;margin:0 auto">'
        f"{body_p('正文。')}</section>"
    )
    efs_err, _, _ = validate_article.validate(empty_first_style)
    assert_true(
        any("style" in e.lower() for e in efs_err),
        f"首个空 style 应视为无样式: {efs_err}",
    )

    empty_semi = (
        '<section style=";">'
        '<p style=";"><span leaf="">正文。</span></p></section>'
    )
    esemi_err, _, _ = validate_article.validate(empty_semi)
    assert_true(
        any("style" in e.lower() for e in esemi_err),
        f"style=';' 应视为无声明: {esemi_err}",
    )

    empty_comment_style = (
        '<section style="/* empty */">'
        '<p style="/* empty */"><span leaf="">正文。</span></p></section>'
    )
    ecom_err, _, _ = validate_article.validate(empty_comment_style)
    assert_true(
        any("style" in e.lower() for e in ecom_err),
        f"style='/* empty */' 应视为无声明: {ecom_err}",
    )

    png_named = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<img src="data:image/png;name=diagram.svg.png;base64,iVBORw0KGgo=">'
        '<span leaf="">图。</span></p>'
    )
    png_err, _, _ = validate_article.validate(png_named)
    assert_true(
        not any("可执行" in e for e in png_err),
        f"png data URI 参数含 svg 不应判为可执行: {png_err}",
    )

    json_xml_profile = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<a href="data:application/json;profile=https://example/xml,{}">'
        '<span leaf="">链。</span></a></p>'
    )
    json_err, _, _ = validate_article.validate(json_xml_profile)
    assert_true(
        not any("可执行" in e for e in json_err),
        f"json data URI 参数含 xml 不应判为可执行: {json_err}",
    )

    svg_img = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<img src="data:image/svg+xml;utf8,<svg></svg>">'
        '<span leaf="">图。</span></p>'
    )
    svg_img_err, _, _ = validate_article.validate(svg_img)
    assert_true(
        any("可执行" in e for e in svg_img_err),
        f"image/svg+xml data URI 仍应失败: {svg_img_err}",
    )

    svg_object = styled_root(
        f"{body_p('正文。')}<object data=\"data:image/svg+xml,<svg onload=alert(1)>\"></object>"
    )
    so_err, _, _ = validate_article.validate(svg_object)
    assert_true(
        any("object" in e.lower() or "禁止" in e or "可执行" in e for e in so_err),
        f"svg data URI object 应失败: {so_err}",
    )

    cdata_script = (
        '<section style="max-width:677px;margin:0 auto">'
        f"{body_p('正文。')}<![CDATA[><script>alert(1)</script></section>"
    )
    cd_err, _, _ = validate_article.validate(cdata_script)
    assert_true(
        any("CDATA" in e or "script" in e.lower() or "声明" in e for e in cd_err),
        f"残缺 CDATA+script 应失败: {cd_err}",
    )

    bom_html = "\ufeff" + (SCRIPTS / "testdata" / "valid_article.html").read_text(encoding="utf-8")
    bom_err, bom_warn, _ = validate_article.validate(bom_html)
    assert_true(not bom_err, f"UTF-8 BOM 不应导致合法正文失败: {bom_err}")

    wrapped_doc = (
        "<html><body>"
        + styled_root(body_p("正文。"))
        + "</body></html>"
    )
    w_err, _, _ = validate_article.validate(wrapped_doc)
    assert_true(any("html" in e.lower() or "body" in e.lower() or "片段" in e for e in w_err), f"完整文档应失败: {w_err}")

    meta_refresh = styled_root(
        f'{body_p("正文。")}<meta http-equiv="refresh" content="0;url=https://attacker.example">'
    )
    meta_err, _, _ = validate_article.validate(meta_refresh)
    assert_true(any("meta" in e.lower() for e in meta_err), f"<meta> 应失败: {meta_err}")

    stray_div = styled_root(f"{body_p('正文。')}</div>")
    stray_err, _, _ = validate_article.validate(stray_div)
    assert_true(any("div" in e.lower() for e in stray_err), f"游离 </div> 应失败: {stray_err}")

    p_root = body_p("正文。")
    pr_err, _, _ = validate_article.validate(p_root)
    assert_true(any("section" in e for e in pr_err), f"非 section 根节点应失败: {pr_err}")

    selfclose_leaf = styled_root(
        '<span leaf=""/ ></span>'
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">中文。</p>'
    )
    sc_err, _, _ = validate_article.validate(selfclose_leaf)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in sc_err),
        f"非 void 自闭合 span[leaf] 不应把后续中文算作已包裹: {sc_err}",
    )

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

        no_html = Path(tmp) / "no-html-pack"
        write_mini_theme(no_html)
        md = (no_html / "THEME.md").read_text(encoding="utf-8")
        (no_html / "THEME.md").write_text(re.sub(r"```html\n.*?```", "", md, flags=re.S), encoding="utf-8")
        nh_err, _ = lint_theme.lint_theme(no_html, schema)
        assert_has(nh_err, "缺少 html 代码块", "槽位无 HTML 围栏应失败")

        empty_sigs = Path(tmp) / "empty-sigs-pack"
        write_mini_theme(empty_sigs)
        payload = json.loads((empty_sigs / "theme.json").read_text(encoding="utf-8"))
        payload["signature_slots"] = []
        (empty_sigs / "theme.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        es_err, _ = lint_theme.lint_theme(empty_sigs, schema)
        assert_true(
            any("signature_slots" in e for e in es_err),
            f"空 signature_slots 应失败: {es_err}",
        )

        unwrap = Path(tmp) / "unwrap-pack"
        write_mini_theme(unwrap)
        umd = (unwrap / "THEME.md").read_text(encoding="utf-8")
        (unwrap / "THEME.md").write_text(
            umd.replace('<span leaf="">{{paragraph}}</span>', '<span leaf="">{{label}}</span>{{body}}', 1),
            encoding="utf-8",
        )
        uw_err, _ = lint_theme.lint_theme(unwrap, schema)
        assert_true(any("span[leaf]" in e or "未包" in e for e in uw_err), f"未包裹占位应失败: {uw_err}")

        no_preview = Path(tmp) / "no-preview-slot"
        write_mini_theme(no_preview)
        preview = (no_preview / "preview.html").read_text(encoding="utf-8")
        (no_preview / "preview.html").write_text(preview.replace("slot:footer", "slot:missing-footer"), encoding="utf-8")
        np_err, _ = lint_theme.lint_theme(no_preview, schema)
        assert_has(np_err, "slot:footer", "预览缺必选槽应失败")

        floated = Path(tmp) / "float-pack"
        write_mini_theme(floated)
        fmd = (floated / "THEME.md").read_text(encoding="utf-8")
        (floated / "THEME.md").write_text(
            fmd.replace('style="max-width:677px;', 'style="float:left;max-width:677px;', 1),
            encoding="utf-8",
        )
        fl_err, _ = lint_theme.lint_theme(floated, schema)
        assert_true(any("float" in e.lower() for e in fl_err), f"主题 float 应失败: {fl_err}")

        no_recipe = Path(tmp) / "no-recipe-pack"
        write_mini_theme(no_recipe)
        rmd = (no_recipe / "THEME.md").read_text(encoding="utf-8")
        (no_recipe / "THEME.md").write_text(rmd.replace("- `tutorial`: hero + h2 + paragraph\n", ""), encoding="utf-8")
        nr_err, _ = lint_theme.lint_theme(no_recipe, schema)
        assert_has(nr_err, "tutorial", "缺文章类型配方应失败")

        named_recipe = Path(tmp) / "named-recipe-pack"
        write_mini_theme(named_recipe)
        nrmd = (named_recipe / "THEME.md").read_text(encoding="utf-8")
        nrmd = nrmd.replace(
            "## 文章类型配方\n\n",
            "## 文章类型配方\n\n本配方覆盖 tutorial 等场景。\n- `not-tutorial`: hero + h2\n",
        )
        nrmd = nrmd.replace("- `tutorial`: hero + h2 + paragraph\n", "")
        (named_recipe / "THEME.md").write_text(nrmd, encoding="utf-8")
        named_err, _ = lint_theme.lint_theme(named_recipe, schema)
        assert_has(named_err, "tutorial", "仅提及 tutorial 不算配方")

        mention_heading = Path(tmp) / "mention-heading-pack"
        write_mini_theme(mention_heading)
        mh = (mention_heading / "THEME.md").read_text(encoding="utf-8")
        mh = mh.replace("## 文章类型配方\n", "说明见 ## 文章类型配方 的写法。\n\n## 文章类型配方\n")
        (mention_heading / "THEME.md").write_text(mh, encoding="utf-8")
        mh_err, _ = lint_theme.lint_theme(mention_heading, schema)
        assert_true(not mh_err, f"正文提到章节名不应误伤配方: {mh_err}")

        notes_fence = Path(tmp) / "notes-fence-pack"
        write_mini_theme(notes_fence)
        nf = (notes_fence / "THEME.md").read_text(encoding="utf-8")
        nf = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n### Notes\n\n```html\n<p style=\"font-size:16px;\"><span leaf=\"\">备注</span></p>\n```\n",
            nf,
            count=1,
            flags=re.S,
        )
        (notes_fence / "THEME.md").write_text(nf, encoding="utf-8")
        nf_err, _ = lint_theme.lint_theme(notes_fence, schema)
        assert_true(any("slot:footer" in e and "html" in e for e in nf_err), f"### Notes 围栏不应算作槽位: {nf_err}")

        prefix_preview = Path(tmp) / "prefix-preview-pack"
        write_mini_theme(prefix_preview)
        pp = (prefix_preview / "preview.html").read_text(encoding="utf-8")
        (prefix_preview / "preview.html").write_text(pp.replace("sig:sig-demo-1", "sig:sig-demo-10"), encoding="utf-8")
        pp_err, _ = lint_theme.lint_theme(prefix_preview, schema)
        assert_true(any("sig:sig-demo-1" in e for e in pp_err), f"预览前缀命中不应放过缺槽: {pp_err}")

        comment_preview = Path(tmp) / "comment-preview-pack"
        write_mini_theme(comment_preview)
        cp = (comment_preview / "preview.html").read_text(encoding="utf-8")
        (comment_preview / "preview.html").write_text(
            cp.replace("<p>slot:footer</p>", "<!-- slot:footer -->"),
            encoding="utf-8",
        )
        cp_err, _ = lint_theme.lint_theme(comment_preview, schema)
        assert_has(cp_err, "slot:footer", "注释里的预览标记不算覆盖")

        script_preview = Path(tmp) / "script-preview-pack"
        write_mini_theme(script_preview)
        sp = (script_preview / "preview.html").read_text(encoding="utf-8")
        (script_preview / "preview.html").write_text(
            sp.replace("<p>slot:footer</p>", "<script>var x='slot:footer'</script>"),
            encoding="utf-8",
        )
        sp_err, _ = lint_theme.lint_theme(script_preview, schema)
        assert_has(sp_err, "slot:footer", "script 字符串里的预览标记不算覆盖")

        template_preview = Path(tmp) / "template-preview-pack"
        write_mini_theme(template_preview)
        tp = (template_preview / "preview.html").read_text(encoding="utf-8")
        (template_preview / "preview.html").write_text(
            tp.replace("<p>slot:footer</p>", "<template><p>slot:footer</p></template>"),
            encoding="utf-8",
        )
        tp_err, _ = lint_theme.lint_theme(template_preview, schema)
        assert_has(tp_err, "slot:footer", "template 里的预览标记不算覆盖")

        hidden_preview = Path(tmp) / "hidden-preview-pack"
        write_mini_theme(hidden_preview)
        hp = (hidden_preview / "preview.html").read_text(encoding="utf-8")
        (hidden_preview / "preview.html").write_text(
            hp.replace("<p>slot:footer</p>", '<p hidden>slot:footer</p>'),
            encoding="utf-8",
        )
        hp_err, _ = lint_theme.lint_theme(hidden_preview, schema)
        assert_has(hp_err, "slot:footer", "hidden 子树里的预览标记不算覆盖")

        css_hidden_preview = Path(tmp) / "css-hidden-preview-pack"
        write_mini_theme(css_hidden_preview)
        chp = (css_hidden_preview / "preview.html").read_text(encoding="utf-8")
        (css_hidden_preview / "preview.html").write_text(
            chp.replace("<p>slot:footer</p>", '<p style="display:none">slot:footer</p>'),
            encoding="utf-8",
        )
        chp_err, _ = lint_theme.lint_theme(css_hidden_preview, schema)
        assert_has(chp_err, "slot:footer", "display:none 的预览标记不算覆盖")

        vis_hidden_preview = Path(tmp) / "vis-hidden-preview-pack"
        write_mini_theme(vis_hidden_preview)
        vhp = (vis_hidden_preview / "preview.html").read_text(encoding="utf-8")
        (vis_hidden_preview / "preview.html").write_text(
            vhp.replace(
                "<p>slot:footer</p>",
                '<p style="visibility:/* x */hidden">slot:footer</p>',
            ),
            encoding="utf-8",
        )
        vhp_err, _ = lint_theme.lint_theme(vis_hidden_preview, schema)
        assert_has(vhp_err, "slot:footer", "visibility:hidden 的预览标记不算覆盖")

        split_preview = Path(tmp) / "split-preview-pack"
        write_mini_theme(split_preview)
        slp = (split_preview / "preview.html").read_text(encoding="utf-8")
        (split_preview / "preview.html").write_text(
            slp.replace("<p>slot:footer</p>", "<p><span>slot:</span><strong>footer</strong></p>"),
            encoding="utf-8",
        )
        slp_err, _ = lint_theme.lint_theme(split_preview, schema)
        assert_true(not slp_err, f"拆开的可见标记应算覆盖: {slp_err}")

        fenced_md = Path(tmp) / "fenced-md-pack"
        write_mini_theme(fenced_md)
        raw_md = (fenced_md / "THEME.md").read_text(encoding="utf-8")
        (fenced_md / "THEME.md").write_text(f"````markdown\n{raw_md}\n````\n", encoding="utf-8")
        fenced_err, _ = lint_theme.lint_theme(fenced_md, schema)
        assert_true(
            any("缺少章节" in e or "缺少 ### slot:" in e for e in fenced_err),
            f"围栏内的 THEME.md 结构不应算数: {fenced_err}",
        )

        empty_fence = Path(tmp) / "empty-html-fence-pack"
        write_mini_theme(empty_fence)
        ef = (empty_fence / "THEME.md").read_text(encoding="utf-8")
        ef = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```html\n```\n",
            ef,
            count=1,
            flags=re.S,
        )
        (empty_fence / "THEME.md").write_text(ef, encoding="utf-8")
        ef_err, _ = lint_theme.lint_theme(empty_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in ef_err),
            f"空 html 围栏不应算作实现: {ef_err}",
        )

        comment_only_fence = Path(tmp) / "comment-html-fence-pack"
        write_mini_theme(comment_only_fence)
        cof = (comment_only_fence / "THEME.md").read_text(encoding="utf-8")
        cof = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```html\n<!-- <p><span leaf=\"\">x</span></p> -->\n```\n",
            cof,
            count=1,
            flags=re.S,
        )
        (comment_only_fence / "THEME.md").write_text(cof, encoding="utf-8")
        cof_err, _ = lint_theme.lint_theme(comment_only_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in cof_err),
            f"仅含 HTML 注释的围栏不应算作实现: {cof_err}",
        )

        commented_md = Path(tmp) / "commented-md-pack"
        write_mini_theme(commented_md)
        raw_commented = (commented_md / "THEME.md").read_text(encoding="utf-8")
        (commented_md / "THEME.md").write_text(f"<!--\n{raw_commented}\n-->\n", encoding="utf-8")
        commented_err, _ = lint_theme.lint_theme(commented_md, schema)
        assert_true(
            any("缺少章节" in e or "缺少 ### slot:" in e for e in commented_err),
            f"HTML 注释里的 THEME.md 结构不应算数: {commented_err}",
        )

        html_wrapped_md = Path(tmp) / "html-wrapped-md-pack"
        write_mini_theme(html_wrapped_md)
        raw_wrapped = (html_wrapped_md / "THEME.md").read_text(encoding="utf-8")
        (html_wrapped_md / "THEME.md").write_text(f"<div>\n{raw_wrapped}\n</div>\n", encoding="utf-8")
        wrapped_err, _ = lint_theme.lint_theme(html_wrapped_md, schema)
        assert_true(
            any("缺少章节" in e or "缺少 ### slot:" in e for e in wrapped_err),
            f"HTML 块里的 THEME.md 结构不应算数: {wrapped_err}",
        )

        dup_sig = Path(tmp) / "dup-sig-pack"
        write_mini_theme(dup_sig)
        dup_payload = json.loads((dup_sig / "theme.json").read_text(encoding="utf-8"))
        dup_payload["signature_slots"] = ["sig-demo-1"] * 8
        (dup_sig / "theme.json").write_text(json.dumps(dup_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        dmd = (dup_sig / "THEME.md").read_text(encoding="utf-8")
        for i in range(2, 9):
            dmd = dmd.replace(f"### sig:sig-demo-{i}", "### sig:sig-demo-1")
        (dup_sig / "THEME.md").write_text(dmd, encoding="utf-8")
        dup_err, _ = lint_theme.lint_theme(dup_sig, schema)
        assert_true(
            any("重复" in e or "不重复" in e or "含重复项" in e for e in dup_err),
            f"重复签名槽 id 应失败: {dup_err}",
        )

        lint_ok = run_cli([sys.executable, str(SCRIPTS / "lint_theme.py"), str(good_dir)])
        assert_true(lint_ok.returncode == 0, f"lint mini 应通过\n{lint_ok.stdout}{lint_ok.stderr}")

    print("selftest: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
