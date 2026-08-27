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


MINI_RECIPE = "核心槽 hero + h2 + paragraph；可用签名槽 sig-demo-1；不要用 image_gif"


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
        md.append(f"- `{kind}`: {MINI_RECIPE}\n")
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

    xss = styled_root(
        f"{body_p('正文。')}"
        '<img src="missing" onerror="alert(1)" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
    )
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

    url_then_prose = styled_root(body_p("参见 https://example.com/path，后文:错误。"))
    _, url_then_warn, _ = validate_article.validate(url_then_prose)
    assert_true(any("半角" in w for w in url_then_warn), f"URL 后的中文正文半角冒号应警告: {url_then_warn}")

    url_comma_cjk = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<a href="https://example.com"><span leaf="">https://example.com</span></a>'
        '<span leaf="">,然后继续。</span></p>'
    )
    _, uc_warn, _ = validate_article.validate(url_comma_cjk)
    assert_true(any("半角" in w for w in uc_warn), f"链接外的半角逗号应警告: {uc_warn}")

    numeric_prose = styled_root(body_p("会议 12:30 开始，约 1,234 人，比例 16:9。"))
    _, num_warn, _ = validate_article.validate(numeric_prose)
    assert_true(not any("半角" in w for w in num_warn), f"数字字面量中的 ,/: 不应报半角标点: {num_warn}")

    split_punct = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<span leaf="">中文</span><span leaf="">:</span><span leaf="">继续。</span></p>'
    )
    _, sp_warn, _ = validate_article.validate(split_punct)
    assert_true(any("半角" in w for w in sp_warn), f"拆开的半角冒号应警告: {sp_warn}")

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
        '<img src="data:image/png;name=diagram.svg.png;base64,iVBORw0KGgo=" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
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
        '<img src="data:image/svg+xml;utf8,<svg></svg>" '
        'style="max-width:100%;height:auto;display:block;margin:0 auto;">'
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

    stray_p = styled_root(body_p("正文。")) + "</p>"
    stray_p_err, _, _ = validate_article.validate(stray_p)
    assert_true(
        any("顶层" in e or "section" in e for e in stray_p_err),
        f"根 section 后的游离 </p> 应失败: {stray_p_err}",
    )

    stray_br = styled_root(body_p("正文。")) + "</br>"
    stray_br_err, _, _ = validate_article.validate(stray_br)
    assert_true(
        any("顶层" in e or "section" in e for e in stray_br_err),
        f"根 section 后的游离 </br> 应失败: {stray_br_err}",
    )

    leaf_quote = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<span leaf=""><blockquote style="margin:0;font-size:16px;">中文。</blockquote></span></p>'
    )
    lq_err, _, _ = validate_article.validate(leaf_quote)
    assert_true(
        any("块级" in e or "leaf" in e.lower() for e in lq_err),
        f"leaf 内 blockquote 应失败: {lq_err}",
    )

    unstyled_h4 = styled_root('<h4><span leaf="">中文。</span></h4>')
    uh4_err, _, _ = validate_article.validate(unstyled_h4)
    assert_true(
        any("style" in e.lower() and ("h4" in e.lower() or "缺少" in e) for e in uh4_err),
        f"无 style 的 h4 应失败: {uh4_err}",
    )

    mismatch_heading = styled_root(
        '<h1 style="font-size:22px;margin:0;"><span leaf="">一。</h2>二。</span></h1>'
    )
    mh_err, _, _ = validate_article.validate(mismatch_heading)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in mh_err),
        f"</h2> 应闭合 h1，二。须未包裹: {mh_err}",
    )

    unstyled_article = styled_root('<article><span leaf="">中文。</span></article>')
    ua_err, _, _ = validate_article.validate(unstyled_article)
    assert_true(
        any("style" in e.lower() and ("article" in e.lower() or "缺少" in e) for e in ua_err),
        f"无 style 的 article 应失败: {ua_err}",
    )

    legacy_image = styled_root(
        '<image style="font-family:monospace;max-width:100%;height:auto;display:block;">'
        + body_p('他说"你好"。')
    )
    _, lim_warn, _ = validate_article.validate(legacy_image)
    assert_true(
        any("半角" in w for w in lim_warn),
        f"<image> 等宽不应把后续正文当代码: {lim_warn}",
    )

    selfclose_leaf = styled_root(
        '<span leaf=""/ ></span>'
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">中文。</p>'
    )
    sc_err, _, _ = validate_article.validate(selfclose_leaf)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in sc_err),
        f"非 void 自闭合 span[leaf] 不应把后续中文算作已包裹: {sc_err}",
    )

    unstyled_media = styled_root(
        '<figure style="margin:0">'
        '<img src="x">'
        '<figcaption><span leaf="">中文。</span></figcaption>'
        "</figure>"
    )
    um_err, _, _ = validate_article.validate(unstyled_media)
    assert_true(
        any("style" in e.lower() and ("img" in e.lower() or "figcaption" in e.lower() or "缺少" in e) for e in um_err),
        f"无 style 的 img/figcaption 应失败: {um_err}",
    )

    unstyled_li = styled_root(
        '<ul style="margin:0 0 16px;padding-left:1.4em;">'
        '<li><span leaf="">中文。</span></li>'
        "</ul>"
    )
    uli_err, _, _ = validate_article.validate(unstyled_li)
    assert_true(
        any("style" in e.lower() and ("li" in e.lower() or "缺少" in e) for e in uli_err),
        f"无 style 的 li 应失败: {uli_err}",
    )

    implied_li = styled_root(
        '<ul style="margin:0 0 16px;padding-left:1.4em;">'
        '<li style="margin:0;font-size:16px;"><span leaf="">一。'
        '<li style="margin:0;font-size:16px;">二。</li></ul>'
    )
    ili_err, _, _ = validate_article.validate(implied_li)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in ili_err),
        f"省略 </li> 时后一项中文不应算已包裹: {ili_err}",
    )

    li_in_quote = styled_root(
        '<ul style="margin:0 0 16px;padding-left:1.4em;">'
        '<li style="margin:0;font-size:16px;"><blockquote style="margin:0;font-size:16px;">'
        '<span leaf="">一。'
        '<li style="margin:0;font-size:16px;">二。</li></ul>'
    )
    liq_err, _, _ = validate_article.validate(li_in_quote)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in liq_err),
        f"blockquote 内省略 </li> 后中文不应算已包裹: {liq_err}",
    )

    code_li_p = styled_root(
        '<ul style="margin:0 0 16px;padding-left:1.4em;">'
        '<li style="margin:0;font-family:Consolas,Monaco,monospace;font-size:13px;">'
        '<p style="margin:0;font-size:13px;"><span leaf="">调用 print("x")。</span></p>'
        "</li></ul>"
    )
    _, clp_warn, _ = validate_article.validate(code_li_p)
    assert_true(
        not any("半角" in w for w in clp_warn),
        f"li 内第一段 p 不应丢掉代码样式: {clp_warn}",
    )

    p_then_quote = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<span leaf="">一。'
        '<blockquote style="margin:0 0 16px;font-size:16px;">二。</blockquote>'
        "</span></p>"
    )
    pq_err, _, _ = validate_article.validate(p_then_quote)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in pq_err),
        f"blockquote 隐含闭合 p 后中文不应算已包裹: {pq_err}",
    )

    p_then_li = styled_root(
        '<ul style="margin:0 0 16px;padding-left:1.4em;">'
        '<p style="margin:0;font-size:16px;"><span leaf="">一。'
        '<li style="margin:0;font-size:16px;">二。</li></ul>'
    )
    pli_err, _, _ = validate_article.validate(p_then_li)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in pli_err),
        f"li 隐含闭合 p 后中文不应算已包裹: {pli_err}",
    )

    nested_a = styled_root(
        '<p style="font-size:16px;margin:0 0 16px;color:#1F2937;">'
        '<a><span leaf="">一。<a>二。</a></span></a></p>'
    )
    na_err, _, _ = validate_article.validate(nested_a)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in na_err),
        f"嵌套 a 清栈后中文不应算已包裹: {na_err}",
    )

    table_foster = styled_root(
        '<table style="width:100%;border-collapse:collapse;">'
        '<span leaf="">'
        '<tr style="font-size:16px;">'
        '<td style="font-size:16px;padding:8px;">中文。</td>'
        "</tr></table>"
    )
    tf_err, _, _ = validate_article.validate(table_foster)
    assert_true(
        any("包裹" in e or "leaf" in e.lower() for e in tf_err),
        f"table 清栈后单元格中文不应算已包裹: {tf_err}",
    )

    pos_comment = (
        '<section style="position/**/:fixed;max-width:677px;margin:0 auto">'
        f"{body_p('正文。')}</section>"
    )
    pc_err, _, _ = validate_article.validate(pos_comment)
    assert_true(
        any("position" in e.lower() or "fixed" in e.lower() for e in pc_err),
        f"CSS 注释拆开的 position:fixed 应失败: {pc_err}",
    )

    pos_escape = (
        '<section style="pos\\69 tion:fixed;max-width:677px;margin:0 auto">'
        f"{body_p('正文。')}</section>"
    )
    pe_err, _, _ = validate_article.validate(pos_escape)
    assert_true(
        any("position" in e.lower() or "fixed" in e.lower() for e in pe_err),
        f"CSS 转义的 position:fixed 应失败: {pe_err}",
    )

    template_wrap = styled_root(
        '<template><p style="font-size:16px;margin:0;"><span leaf="">中文。</span></p></template>'
    )
    tw_err, _, _ = validate_article.validate(template_wrap)
    assert_true(any("template" in e.lower() for e in tw_err), f"<template> 应失败: {tw_err}")

    select_wrap = styled_root(
        '<select><option><span leaf="">中文。</span></option></select>'
    )
    sel_err, _, _ = validate_article.validate(select_wrap)
    assert_true(
        any("select" in e.lower() or "option" in e.lower() for e in sel_err),
        f"<select>/<option> 应失败: {sel_err}",
    )

    dialog_wrap = styled_root(
        '<dialog style="margin:0;font-size:16px;"><p style="margin:0;font-size:16px;">'
        '<span leaf="">中文。</span></p></dialog>'
    )
    dlg_err, _, _ = validate_article.validate(dialog_wrap)
    assert_true(
        any("dialog" in e.lower() or "details" in e.lower() or "noscript" in e.lower() for e in dlg_err),
        f"<dialog> 应失败: {dlg_err}",
    )

    details_wrap = styled_root(
        '<details style="margin:0;font-size:16px;"><summary style="font-size:16px;">'
        '<span leaf="">中文。</span></summary></details>'
    )
    det_err, _, _ = validate_article.validate(details_wrap)
    assert_true(
        any("dialog" in e.lower() or "details" in e.lower() or "noscript" in e.lower() for e in det_err),
        f"<details> 应失败: {det_err}",
    )

    noscript_wrap = styled_root(
        '<noscript><p style="margin:0;font-size:16px;"><span leaf="">中文。</span></p></noscript>'
    )
    ns_err, _, _ = validate_article.validate(noscript_wrap)
    assert_true(
        any("dialog" in e.lower() or "details" in e.lower() or "noscript" in e.lower() for e in ns_err),
        f"<noscript> 应失败: {ns_err}",
    )

    void_code_img = styled_root(
        '<img src="https://example.test/a.png" '
        'style="font-family:monospace;max-width:100%;height:auto;display:block;">'
        + body_p('他说"你好"。')
    )
    _, vci_warn, _ = validate_article.validate(void_code_img)
    assert_true(
        any("半角" in w for w in vci_warn),
        f"void 等宽标签不应把后续正文当代码: {vci_warn}",
    )

    base_tag = styled_root(f'{body_p("正文。")}<base href="https://attacker.example/">')
    base_err, _, _ = validate_article.validate(base_tag)
    assert_true(any("base" in e.lower() for e in base_err), f"<base> 应失败: {base_err}")

    plaintext_tag = styled_root(f"{body_p('正文。')}<plaintext>")
    pt_err, _, _ = validate_article.validate(plaintext_tag)
    assert_true(
        any("plaintext" in e.lower() or "预览" in e for e in pt_err),
        f"<plaintext> 应失败: {pt_err}",
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
        (no_recipe / "THEME.md").write_text(rmd.replace(f"- `tutorial`: {MINI_RECIPE}\n", ""), encoding="utf-8")
        nr_err, _ = lint_theme.lint_theme(no_recipe, schema)
        assert_has(nr_err, "tutorial", "缺文章类型配方应失败")

        named_recipe = Path(tmp) / "named-recipe-pack"
        write_mini_theme(named_recipe)
        nrmd = (named_recipe / "THEME.md").read_text(encoding="utf-8")
        nrmd = nrmd.replace(
            "## 文章类型配方\n\n",
            "## 文章类型配方\n\n本配方覆盖 tutorial 等场景。\n- `not-tutorial`: hero + h2\n",
        )
        nrmd = nrmd.replace("- `tutorial`: " + MINI_RECIPE + "\n", "")
        (named_recipe / "THEME.md").write_text(nrmd, encoding="utf-8")
        named_err, _ = lint_theme.lint_theme(named_recipe, schema)
        assert_has(named_err, "tutorial", "仅提及 tutorial 不算配方")

        name_only_recipe = Path(tmp) / "name-only-recipe-pack"
        write_mini_theme(name_only_recipe)
        nord = (name_only_recipe / "THEME.md").read_text(encoding="utf-8")
        for kind in lint_theme.ARTICLE_TYPES:
            nord = nord.replace(f"- `{kind}`: {MINI_RECIPE}\n", f"- {kind}\n")
        (name_only_recipe / "THEME.md").write_text(nord, encoding="utf-8")
        nord_err, _ = lint_theme.lint_theme(name_only_recipe, schema)
        assert_has(nord_err, "tutorial", "仅有类型名的列表项不算配方")

        plain_recipe = Path(tmp) / "plain-recipe-pack"
        write_mini_theme(plain_recipe)
        prd = (plain_recipe / "THEME.md").read_text(encoding="utf-8")
        for kind in lint_theme.ARTICLE_TYPES:
            prd = prd.replace(f"- `{kind}`: {MINI_RECIPE}\n", f"{kind}：{MINI_RECIPE}\n")
        (plain_recipe / "THEME.md").write_text(prd, encoding="utf-8")
        plain_err, _ = lint_theme.lint_theme(plain_recipe, schema)
        assert_true(not plain_err, f"普通配方行应通过: {plain_err}")

        paren_recipe = Path(tmp) / "paren-recipe-pack"
        write_mini_theme(paren_recipe)
        pnd = (paren_recipe / "THEME.md").read_text(encoding="utf-8")
        for i, kind in enumerate(lint_theme.ARTICLE_TYPES, 1):
            pnd = pnd.replace(f"- `{kind}`: {MINI_RECIPE}\n", f"{i}) {kind}: {MINI_RECIPE}\n")
        (paren_recipe / "THEME.md").write_text(pnd, encoding="utf-8")
        paren_err, _ = lint_theme.lint_theme(paren_recipe, schema)
        assert_true(not paren_err, f"括号有序列表配方应通过: {paren_err}")

        stub_recipe = Path(tmp) / "stub-recipe-pack"
        write_mini_theme(stub_recipe)
        srd = (stub_recipe / "THEME.md").read_text(encoding="utf-8")
        for kind in lint_theme.ARTICLE_TYPES:
            srd = srd.replace(f"- `{kind}`: {MINI_RECIPE}\n", f"- `{kind}`: x\n")
        (stub_recipe / "THEME.md").write_text(srd, encoding="utf-8")
        stub_err, _ = lint_theme.lint_theme(stub_recipe, schema)
        assert_has(stub_err, "tutorial", "仅有单字符说明的配方不算覆盖")

        vague_recipe = Path(tmp) / "vague-recipe-pack"
        write_mini_theme(vague_recipe)
        vrd = (vague_recipe / "THEME.md").read_text(encoding="utf-8")
        for kind in lint_theme.ARTICLE_TYPES:
            vrd = vrd.replace(
                f"- `{kind}`: {MINI_RECIPE}\n",
                f"- `{kind}`: root + 签名槽 + 不要用的槽\n",
            )
        (vague_recipe / "THEME.md").write_text(vrd, encoding="utf-8")
        vrd_err, _ = lint_theme.lint_theme(vague_recipe, schema)
        assert_has(vrd_err, "tutorial", "仅有「签名槽」「不要用的槽」字样不算配方")

        indented_recipe = Path(tmp) / "indented-recipe-pack"
        write_mini_theme(indented_recipe)
        ird = (indented_recipe / "THEME.md").read_text(encoding="utf-8")
        for kind in lint_theme.ARTICLE_TYPES:
            ird = ird.replace(
                f"- `{kind}`: {MINI_RECIPE}\n",
                f"    {kind}: {MINI_RECIPE}\n",
            )
        (indented_recipe / "THEME.md").write_text(ird, encoding="utf-8")
        ird_err, _ = lint_theme.lint_theme(indented_recipe, schema)
        assert_has(ird_err, "tutorial", "缩进代码块里的配方行不算覆盖")

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

        left_boundary_preview = Path(tmp) / "left-boundary-preview-pack"
        write_mini_theme(left_boundary_preview)
        lbp = (left_boundary_preview / "preview.html").read_text(encoding="utf-8")
        (left_boundary_preview / "preview.html").write_text(
            lbp.replace("<p>slot:footer</p>", "<p>missing-slot:footer</p>"),
            encoding="utf-8",
        )
        lbp_err, _ = lint_theme.lint_theme(left_boundary_preview, schema)
        assert_has(lbp_err, "slot:footer", "左侧无边界的 slot:footer 不算覆盖")

        preview_slot_prefix = Path(tmp) / "preview-slot-prefix-pack"
        write_mini_theme(preview_slot_prefix)
        psp = (preview_slot_prefix / "preview.html").read_text(encoding="utf-8")
        (preview_slot_prefix / "preview.html").write_text(
            psp.replace("<p>slot:footer</p>", "<p>not-preview-slot-footer</p>"),
            encoding="utf-8",
        )
        psp_err, _ = lint_theme.lint_theme(preview_slot_prefix, schema)
        assert_has(psp_err, "slot:footer", "左侧无边界的 preview-slot-footer 不算覆盖")

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

        css_var_preview = Path(tmp) / "css-var-preview-pack"
        write_mini_theme(css_var_preview)
        cvp = (css_var_preview / "preview.html").read_text(encoding="utf-8")
        (css_var_preview / "preview.html").write_text(
            cvp.replace(
                "<p>slot:footer</p>",
                '<p style="--example:display:none">slot:footer</p>',
            ),
            encoding="utf-8",
        )
        cvp_err, _ = lint_theme.lint_theme(css_var_preview, schema)
        assert_true(not cvp_err, f"自定义属性里的 display:none 文本不应误判隐藏: {cvp_err}")

        void_hidden_preview = Path(tmp) / "void-hidden-preview-pack"
        write_mini_theme(void_hidden_preview)
        vhp2 = (void_hidden_preview / "preview.html").read_text(encoding="utf-8")
        (void_hidden_preview / "preview.html").write_text(
            vhp2.replace("<p>slot:footer</p>", '<img hidden><p>slot:footer</p>'),
            encoding="utf-8",
        )
        vhp2_err, _ = lint_theme.lint_theme(void_hidden_preview, schema)
        assert_true(not vhp2_err, f"hidden 的 void 标签不应把后续可见标记吃掉: {vhp2_err}")

        hidden_input_preview = Path(tmp) / "hidden-input-preview-pack"
        write_mini_theme(hidden_input_preview)
        hip = (hidden_input_preview / "preview.html").read_text(encoding="utf-8")
        (hidden_input_preview / "preview.html").write_text(
            hip.replace("<p>slot:footer</p>", '<input type="hidden" name="slot:footer">'),
            encoding="utf-8",
        )
        hip_err, _ = lint_theme.lint_theme(hidden_input_preview, schema)
        assert_has(hip_err, "slot:footer", "hidden input 的 name 不算预览覆盖")

        closed_dialog_preview = Path(tmp) / "closed-dialog-preview-pack"
        write_mini_theme(closed_dialog_preview)
        cdp = (closed_dialog_preview / "preview.html").read_text(encoding="utf-8")
        (closed_dialog_preview / "preview.html").write_text(
            cdp.replace("<p>slot:footer</p>", "<dialog><p>slot:footer</p></dialog>"),
            encoding="utf-8",
        )
        cdp_err, _ = lint_theme.lint_theme(closed_dialog_preview, schema)
        assert_has(cdp_err, "slot:footer", "未 open 的 dialog 里的标记不算覆盖")

        closed_details_preview = Path(tmp) / "closed-details-preview-pack"
        write_mini_theme(closed_details_preview)
        cdt = (closed_details_preview / "preview.html").read_text(encoding="utf-8")
        (closed_details_preview / "preview.html").write_text(
            cdt.replace(
                "<p>slot:footer</p>",
                "<details><summary>More</summary><p>slot:footer</p></details>",
            ),
            encoding="utf-8",
        )
        cdt_err, _ = lint_theme.lint_theme(closed_details_preview, schema)
        assert_has(cdt_err, "slot:footer", "关闭的 details 里非 summary 标记不算覆盖")

        second_summary_preview = Path(tmp) / "second-summary-preview-pack"
        write_mini_theme(second_summary_preview)
        ssp = (second_summary_preview / "preview.html").read_text(encoding="utf-8")
        (second_summary_preview / "preview.html").write_text(
            ssp.replace(
                "<p>slot:footer</p>",
                "<details><summary>More</summary><summary>slot:footer</summary></details>",
            ),
            encoding="utf-8",
        )
        ssp_err, _ = lint_theme.lint_theme(second_summary_preview, schema)
        assert_has(ssp_err, "slot:footer", "关闭 details 的第二个 summary 不算覆盖")

        nested_then_direct_summary = Path(tmp) / "nested-then-direct-summary-pack"
        write_mini_theme(nested_then_direct_summary)
        ntds = (nested_then_direct_summary / "preview.html").read_text(encoding="utf-8")
        (nested_then_direct_summary / "preview.html").write_text(
            ntds.replace(
                "<p>slot:footer</p>",
                "<details><div><summary>Other</summary></div><summary>slot:footer</summary></details>",
            ),
            encoding="utf-8",
        )
        ntds_err, _ = lint_theme.lint_theme(nested_then_direct_summary, schema)
        assert_true(
            not any("slot:footer" in e for e in ntds_err),
            f"关闭 details 的第一个直接 summary 应算覆盖: {ntds_err}",
        )

        meta_preview = Path(tmp) / "meta-preview-pack"
        write_mini_theme(meta_preview)
        mpv = (meta_preview / "preview.html").read_text(encoding="utf-8")
        (meta_preview / "preview.html").write_text(
            mpv.replace("<p>slot:footer</p>", '<meta name="slot:footer">'),
            encoding="utf-8",
        )
        mpv_err, _ = lint_theme.lint_theme(meta_preview, schema)
        assert_has(mpv_err, "slot:footer", "meta 上的预览标记不算覆盖")

        source_preview = Path(tmp) / "source-preview-pack"
        write_mini_theme(source_preview)
        srcp = (source_preview / "preview.html").read_text(encoding="utf-8")
        (source_preview / "preview.html").write_text(
            srcp.replace("<p>slot:footer</p>", '<source id="slot:footer">'),
            encoding="utf-8",
        )
        srcp_err, _ = lint_theme.lint_theme(source_preview, schema)
        assert_has(srcp_err, "slot:footer", "source 上的预览标记不算覆盖")

        opacity_preview = Path(tmp) / "opacity-preview-pack"
        write_mini_theme(opacity_preview)
        opp = (opacity_preview / "preview.html").read_text(encoding="utf-8")
        (opacity_preview / "preview.html").write_text(
            opp.replace("<p>slot:footer</p>", '<p style="opacity:0">slot:footer</p>'),
            encoding="utf-8",
        )
        opp_err, _ = lint_theme.lint_theme(opacity_preview, schema)
        assert_has(opp_err, "slot:footer", "opacity:0 的预览标记不算覆盖")

        opacity_pct_preview = Path(tmp) / "opacity-pct-preview-pack"
        write_mini_theme(opacity_pct_preview)
        oppp = (opacity_pct_preview / "preview.html").read_text(encoding="utf-8")
        (opacity_pct_preview / "preview.html").write_text(
            oppp.replace("<p>slot:footer</p>", '<p style="opacity:0%">slot:footer</p>'),
            encoding="utf-8",
        )
        oppp_err, _ = lint_theme.lint_theme(opacity_pct_preview, schema)
        assert_has(oppp_err, "slot:footer", "opacity:0% 的预览标记不算覆盖")

        opacity_override_preview = Path(tmp) / "opacity-override-preview-pack"
        write_mini_theme(opacity_override_preview)
        opo = (opacity_override_preview / "preview.html").read_text(encoding="utf-8")
        (opacity_override_preview / "preview.html").write_text(
            opo.replace("<p>slot:footer</p>", '<p style="opacity:0;opacity:1">slot:footer</p>'),
            encoding="utf-8",
        )
        opo_err, _ = lint_theme.lint_theme(opacity_override_preview, schema)
        assert_true(
            not any("slot:footer" in e for e in opo_err),
            f"后声明 opacity:1 的标记应算覆盖: {opo_err}",
        )

        display_override_preview = Path(tmp) / "display-override-preview-pack"
        write_mini_theme(display_override_preview)
        dvo = (display_override_preview / "preview.html").read_text(encoding="utf-8")
        (display_override_preview / "preview.html").write_text(
            dvo.replace("<p>slot:footer</p>", '<p style="display:none;display:block">slot:footer</p>'),
            encoding="utf-8",
        )
        dvo_err, _ = lint_theme.lint_theme(display_override_preview, schema)
        assert_true(
            not any("slot:footer" in e for e in dvo_err),
            f"后声明 display:block 的标记应算覆盖: {dvo_err}",
        )

        vis_override_preview = Path(tmp) / "vis-override-preview-pack"
        write_mini_theme(vis_override_preview)
        viso = (vis_override_preview / "preview.html").read_text(encoding="utf-8")
        (vis_override_preview / "preview.html").write_text(
            viso.replace(
                "<p>slot:footer</p>",
                '<div style="visibility:hidden"><p style="visibility:visible">slot:footer</p></div>',
            ),
            encoding="utf-8",
        )
        viso_err, _ = lint_theme.lint_theme(vis_override_preview, schema)
        assert_true(
            not any("slot:footer" in e for e in viso_err),
            f"子元素 visibility:visible 应覆盖祖先 hidden: {viso_err}",
        )

        param_preview = Path(tmp) / "param-preview-pack"
        write_mini_theme(param_preview)
        prm = (param_preview / "preview.html").read_text(encoding="utf-8")
        (param_preview / "preview.html").write_text(
            prm.replace("<p>slot:footer</p>", '<param id="slot:footer">'),
            encoding="utf-8",
        )
        prm_err, _ = lint_theme.lint_theme(param_preview, schema)
        assert_has(prm_err, "slot:footer", "param 上的预览标记不算覆盖")

        iframe_preview = Path(tmp) / "iframe-preview-pack"
        write_mini_theme(iframe_preview)
        ifp = (iframe_preview / "preview.html").read_text(encoding="utf-8")
        (iframe_preview / "preview.html").write_text(
            ifp.replace("<p>slot:footer</p>", "<iframe>slot:footer</iframe>"),
            encoding="utf-8",
        )
        ifp_err, _ = lint_theme.lint_theme(iframe_preview, schema)
        assert_has(ifp_err, "slot:footer", "iframe 回退文本不算预览覆盖")

        canvas_preview = Path(tmp) / "canvas-preview-pack"
        write_mini_theme(canvas_preview)
        cvsp = (canvas_preview / "preview.html").read_text(encoding="utf-8")
        (canvas_preview / "preview.html").write_text(
            cvsp.replace("<p>slot:footer</p>", "<canvas>slot:footer</canvas>"),
            encoding="utf-8",
        )
        cvsp_err, _ = lint_theme.lint_theme(canvas_preview, schema)
        assert_has(cvsp_err, "slot:footer", "canvas 回退文本不算预览覆盖")

        sheet_hidden_preview = Path(tmp) / "sheet-hidden-preview-pack"
        write_mini_theme(sheet_hidden_preview)
        shp = (sheet_hidden_preview / "preview.html").read_text(encoding="utf-8")
        shp = shp.replace(
            "</head>",
            "<style>#footer{display:none}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer" data-slot="slot:footer">页脚</p>',
        )
        (sheet_hidden_preview / "preview.html").write_text(shp, encoding="utf-8")
        shp_err, _ = lint_theme.lint_theme(sheet_hidden_preview, schema)
        assert_has(shp_err, "slot:footer", "预览样式表 display:none 的标记不算覆盖")

        stray_td_preview = Path(tmp) / "stray-td-preview-pack"
        write_mini_theme(stray_td_preview)
        stdp = (stray_td_preview / "preview.html").read_text(encoding="utf-8")
        (stray_td_preview / "preview.html").write_text(
            stdp.replace("<p>slot:footer</p>", "<div hidden><td>slot:footer</td></div>"),
            encoding="utf-8",
        )
        stdp_err, _ = lint_theme.lint_theme(stray_td_preview, schema)
        assert_has(stdp_err, "slot:footer", "hidden 祖先里的游离 td 不算覆盖")

        datalist_preview = Path(tmp) / "datalist-preview-pack"
        write_mini_theme(datalist_preview)
        dlp = (datalist_preview / "preview.html").read_text(encoding="utf-8")
        (datalist_preview / "preview.html").write_text(
            dlp.replace(
                "<p>slot:footer</p>",
                '<datalist><option data-slot="slot:footer">Footer</option></datalist>',
            ),
            encoding="utf-8",
        )
        dlp_err, _ = lint_theme.lint_theme(datalist_preview, schema)
        assert_has(dlp_err, "slot:footer", "datalist 子树里的预览标记不算覆盖")

        quoted_attr_sheet = Path(tmp) / "quoted-attr-sheet-pack"
        write_mini_theme(quoted_attr_sheet)
        qas = (quoted_attr_sheet / "preview.html").read_text(encoding="utf-8")
        qas = qas.replace(
            "</head>",
            '<style>[data-label="a b"]{display:none}</style></head>',
        ).replace(
            "<p>slot:footer</p>",
            '<p data-label="a b">slot:footer</p>',
        )
        (quoted_attr_sheet / "preview.html").write_text(qas, encoding="utf-8")
        qas_err, _ = lint_theme.lint_theme(quoted_attr_sheet, schema)
        assert_has(qas_err, "slot:footer", "带空格的属性选择器应能隐藏预览标记")

        comma_attr_sheet = Path(tmp) / "comma-attr-sheet-pack"
        write_mini_theme(comma_attr_sheet)
        cas = (comma_attr_sheet / "preview.html").read_text(encoding="utf-8")
        cas = cas.replace(
            "</head>",
            '<style>[data-label="a,b"]{display:none}</style></head>',
        ).replace(
            "<p>slot:footer</p>",
            '<p data-label="a,b">slot:footer</p>',
        )
        (comma_attr_sheet / "preview.html").write_text(cas, encoding="utf-8")
        cas_err, _ = lint_theme.lint_theme(comma_attr_sheet, schema)
        assert_has(cas_err, "slot:footer", "引号内逗号的属性选择器应能隐藏预览标记")

        hover_sheet = Path(tmp) / "hover-sheet-pack"
        write_mini_theme(hover_sheet)
        hvs = (hover_sheet / "preview.html").read_text(encoding="utf-8")
        hvs = hvs.replace(
            "</head>",
            "<style>#footer:hover{display:none}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer">slot:footer</p>',
        )
        (hover_sheet / "preview.html").write_text(hvs, encoding="utf-8")
        hvs_err, _ = lint_theme.lint_theme(hover_sheet, schema)
        assert_true(
            not any("slot:footer" in e for e in hvs_err),
            f":hover 规则在默认预览下不应隐藏标记: {hvs_err}",
        )

        print_sheet = Path(tmp) / "print-sheet-pack"
        write_mini_theme(print_sheet)
        prs = (print_sheet / "preview.html").read_text(encoding="utf-8")
        prs = prs.replace(
            "</head>",
            '<style media="print">#footer{display:none}</style></head>',
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer">slot:footer</p>',
        )
        (print_sheet / "preview.html").write_text(prs, encoding="utf-8")
        prs_err, _ = lint_theme.lint_theme(print_sheet, schema)
        assert_true(
            not any("slot:footer" in e for e in prs_err),
            f"print 样式表不应作用于屏幕预览: {prs_err}",
        )

        not_hidden_sheet = Path(tmp) / "not-hidden-sheet-pack"
        write_mini_theme(not_hidden_sheet)
        nhs = (not_hidden_sheet / "preview.html").read_text(encoding="utf-8")
        nhs = nhs.replace(
            "</head>",
            "<style>#footer:not(.hidden){display:none}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer" class="hidden">slot:footer</p>',
        )
        (not_hidden_sheet / "preview.html").write_text(nhs, encoding="utf-8")
        nhs_err, _ = lint_theme.lint_theme(not_hidden_sheet, schema)
        assert_true(
            not any("slot:footer" in e for e in nhs_err),
            f":not(.hidden) 在 class=hidden 时不应隐藏标记: {nhs_err}",
        )

        ci_attr_sheet = Path(tmp) / "ci-attr-sheet-pack"
        write_mini_theme(ci_attr_sheet)
        cias = (ci_attr_sheet / "preview.html").read_text(encoding="utf-8")
        cias = cias.replace(
            "</head>",
            '<style>[data-label="FOOT" i]{display:none}</style></head>',
        ).replace(
            "<p>slot:footer</p>",
            '<p data-label="foot" data-slot="slot:footer">页脚</p>',
        )
        (ci_attr_sheet / "preview.html").write_text(cias, encoding="utf-8")
        cias_err, _ = lint_theme.lint_theme(ci_attr_sheet, schema)
        assert_has(cias_err, "slot:footer", "i 修饰符应大小写不敏感匹配属性")

        prefix_attr_sheet = Path(tmp) / "prefix-attr-sheet-pack"
        write_mini_theme(prefix_attr_sheet)
        pas = (prefix_attr_sheet / "preview.html").read_text(encoding="utf-8")
        pas = pas.replace(
            "</head>",
            '<style>[data-label^="foot"]{display:none}</style></head>',
        ).replace(
            "<p>slot:footer</p>",
            '<p data-label="footer" data-slot="slot:footer">页脚</p>',
        )
        (prefix_attr_sheet / "preview.html").write_text(pas, encoding="utf-8")
        pas_err, _ = lint_theme.lint_theme(prefix_attr_sheet, schema)
        assert_has(pas_err, "slot:footer", "属性选择器 ^= 应能隐藏预览标记")

        important_sheet = Path(tmp) / "important-sheet-pack"
        write_mini_theme(important_sheet)
        ims = (important_sheet / "preview.html").read_text(encoding="utf-8")
        ims = ims.replace(
            "</head>",
            "<style>#footer{display:none!important}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer" style="display:block">slot:footer</p>',
        )
        (important_sheet / "preview.html").write_text(ims, encoding="utf-8")
        ims_err, _ = lint_theme.lint_theme(important_sheet, schema)
        assert_has(ims_err, "slot:footer", "样式表 !important 应压过 inline display:block")

        later_visible_sheet = Path(tmp) / "later-visible-sheet-pack"
        write_mini_theme(later_visible_sheet)
        lvs = (later_visible_sheet / "preview.html").read_text(encoding="utf-8")
        lvs = lvs.replace(
            "</head>",
            "<style>#footer{display:none}#footer{display:block}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer">slot:footer</p>',
        )
        (later_visible_sheet / "preview.html").write_text(lvs, encoding="utf-8")
        lvs_err, _ = lint_theme.lint_theme(later_visible_sheet, schema)
        assert_true(
            not any("slot:footer" in e for e in lvs_err),
            f"后出现的 display:block 应覆盖先前的 display:none: {lvs_err}",
        )

        descendant_sheet = Path(tmp) / "descendant-sheet-pack"
        write_mini_theme(descendant_sheet)
        dcs = (descendant_sheet / "preview.html").read_text(encoding="utf-8")
        dcs = dcs.replace(
            "</head>",
            "<style>.hidden #footer{display:none}</style></head>",
        ).replace(
            "<p>slot:footer</p>",
            '<p id="footer">slot:footer</p>',
        )
        (descendant_sheet / "preview.html").write_text(dcs, encoding="utf-8")
        dcs_err, _ = lint_theme.lint_theme(descendant_sheet, schema)
        assert_true(
            not any("slot:footer" in e for e in dcs_err),
            f"无 .hidden 祖先时 .hidden #footer 不应隐藏标记: {dcs_err}",
        )

        select_option_preview = Path(tmp) / "select-option-preview-pack"
        write_mini_theme(select_option_preview)
        sop = (select_option_preview / "preview.html").read_text(encoding="utf-8")
        (select_option_preview / "preview.html").write_text(
            sop.replace(
                "<p>slot:footer</p>",
                '<select><option>可见</option><option data-slot="slot:footer">Footer</option></select>',
            ),
            encoding="utf-8",
        )
        sop_err, _ = lint_theme.lint_theme(select_option_preview, schema)
        assert_has(sop_err, "slot:footer", "未选中的 option 不算预览覆盖")

        stray_br_preview = Path(tmp) / "stray-br-preview-pack"
        write_mini_theme(stray_br_preview)
        sbp = (stray_br_preview / "preview.html").read_text(encoding="utf-8")
        (stray_br_preview / "preview.html").write_text(
            sbp.replace("<p>slot:footer</p>", "<p>slot:</br>footer</p>"),
            encoding="utf-8",
        )
        sbp_err, _ = lint_theme.lint_theme(stray_br_preview, schema)
        assert_has(sbp_err, "slot:footer", "游离 </br> 应打断预览标记拼接")

        stray_p_preview = Path(tmp) / "stray-p-preview-pack"
        write_mini_theme(stray_p_preview)
        spp = (stray_p_preview / "preview.html").read_text(encoding="utf-8")
        (stray_p_preview / "preview.html").write_text(
            spp.replace("<p>slot:footer</p>", "<span>slot:</p>footer</span>"),
            encoding="utf-8",
        )
        spp_err, _ = lint_theme.lint_theme(stray_p_preview, schema)
        assert_has(spp_err, "slot:footer", "游离 </p> 应打断预览标记拼接")

        popover_preview = Path(tmp) / "popover-preview-pack"
        write_mini_theme(popover_preview)
        pvp = (popover_preview / "preview.html").read_text(encoding="utf-8")
        (popover_preview / "preview.html").write_text(
            pvp.replace(
                "<p>slot:footer</p>",
                '<section popover data-slot="slot:footer">slot:footer</section>',
            ),
            encoding="utf-8",
        )
        pvp_err, _ = lint_theme.lint_theme(popover_preview, schema)
        assert_has(pvp_err, "slot:footer", "未打开的 popover 不算预览覆盖")

        tbody_preview = Path(tmp) / "tbody-preview-pack"
        write_mini_theme(tbody_preview)
        tbp = (tbody_preview / "preview.html").read_text(encoding="utf-8")
        (tbody_preview / "preview.html").write_text(
            tbp.replace(
                "<p>slot:footer</p>",
                "<table><tbody hidden><tr><td>note</td></tr><tbody><tr><td>slot:footer</td></tr></table>",
            ),
            encoding="utf-8",
        )
        tbp_err, _ = lint_theme.lint_theme(tbody_preview, schema)
        assert_true(
            not any("slot:footer" in e for e in tbp_err),
            f"后一个 tbody 隐含闭合 hidden 后标记应算覆盖: {tbp_err}",
        )

        implied_hidden_p_preview = Path(tmp) / "implied-hidden-p-preview-pack"
        write_mini_theme(implied_hidden_p_preview)
        ihp = (implied_hidden_p_preview / "preview.html").read_text(encoding="utf-8")
        (implied_hidden_p_preview / "preview.html").write_text(
            ihp.replace("<p>slot:footer</p>", "<p hidden>note<p>slot:footer</p>"),
            encoding="utf-8",
        )
        ihp_err, _ = lint_theme.lint_theme(implied_hidden_p_preview, schema)
        assert_true(
            not any("slot:footer" in e for e in ihp_err),
            f"隐含闭合 hidden p 后的可见标记应算覆盖: {ihp_err}",
        )

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

        br_hero = Path(tmp) / "br-hero-pack"
        write_mini_theme(br_hero)
        bh = (br_hero / "THEME.md").read_text(encoding="utf-8")
        bh = re.sub(
            r"### slot:hero\n\n```html\n.*?```\n",
            "### slot:hero\n\n```html\n<br>\n```\n",
            bh,
            count=1,
            flags=re.S,
        )
        (br_hero / "THEME.md").write_text(bh, encoding="utf-8")
        bh_err, _ = lint_theme.lint_theme(br_hero, schema)
        assert_true(
            any("slot:hero" in e and "可用" in e for e in bh_err),
            f"hero 仅 <br> 不应算作可用内容: {bh_err}",
        )

        incomplete_tag_fence = Path(tmp) / "incomplete-tag-fence-pack"
        write_mini_theme(incomplete_tag_fence)
        itf = (incomplete_tag_fence / "THEME.md").read_text(encoding="utf-8")
        itf = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```html\n<p\n```\n",
            itf,
            count=1,
            flags=re.S,
        )
        (incomplete_tag_fence / "THEME.md").write_text(itf, encoding="utf-8")
        itf_err, _ = lint_theme.lint_theme(incomplete_tag_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in itf_err),
            f"未完成的 <p 不应算作 html 实现: {itf_err}",
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
        compact = "\n".join(line for line in raw_wrapped.splitlines() if line.strip())
        (html_wrapped_md / "THEME.md").write_text(f"<div>\n{compact}\n</div>\n", encoding="utf-8")
        wrapped_err, _ = lint_theme.lint_theme(html_wrapped_md, schema)
        assert_true(
            any("缺少章节" in e or "缺少 ### slot:" in e for e in wrapped_err),
            f"HTML 块里的 THEME.md 结构不应算数: {wrapped_err}",
        )

        unmatched_end_md = Path(tmp) / "unmatched-end-md-pack"
        write_mini_theme(unmatched_end_md)
        uem = (unmatched_end_md / "THEME.md").read_text(encoding="utf-8")
        uem = uem.replace("## 结构模型\n", "<section>\n</span>\n## 结构模型\n")
        (unmatched_end_md / "THEME.md").write_text(uem, encoding="utf-8")
        uem_err, _ = lint_theme.lint_theme(unmatched_end_md, schema)
        assert_true(
            any("结构模型" in e for e in uem_err),
            f"未匹配 </span> 不应露出 HTML 块里的标题: {uem_err}",
        )

        matched_section_md = Path(tmp) / "matched-section-md-pack"
        write_mini_theme(matched_section_md)
        msm = (matched_section_md / "THEME.md").read_text(encoding="utf-8")
        msm = msm.replace("## 结构模型\n", "<section>\n</section>\n## 结构模型\n")
        (matched_section_md / "THEME.md").write_text(msm, encoding="utf-8")
        msm_err, _ = lint_theme.lint_theme(matched_section_md, schema)
        assert_true(
            any("结构模型" in e for e in msm_err),
            f"配对 </section> 不应结束 type-6 HTML 块: {msm_err}",
        )

        html_block_fence = Path(tmp) / "html-block-fence-pack"
        write_mini_theme(html_block_fence)
        hbf = (html_block_fence / "THEME.md").read_text(encoding="utf-8")
        hbf = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n<div>\n```html\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```\n</div>\n",
            hbf,
            count=1,
            flags=re.S,
        )
        (html_block_fence / "THEME.md").write_text(hbf, encoding="utf-8")
        hbf_err, _ = lint_theme.lint_theme(html_block_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in hbf_err),
            f"HTML 块里的围栏不应算作组件实现: {hbf_err}",
        )

        autolink_md = Path(tmp) / "autolink-md-pack"
        write_mini_theme(autolink_md)
        raw_auto = (autolink_md / "THEME.md").read_text(encoding="utf-8")
        (autolink_md / "THEME.md").write_text(f"<https://example.com>\n\n{raw_auto}", encoding="utf-8")
        auto_err, _ = lint_theme.lint_theme(autolink_md, schema)
        assert_true(not auto_err, f"Markdown 自动链接不应吞掉后续结构: {auto_err}")

        autolink_tight = Path(tmp) / "autolink-tight-pack"
        write_mini_theme(autolink_tight)
        raw_tight = (autolink_tight / "THEME.md").read_text(encoding="utf-8")
        raw_tight = raw_tight.replace("## 结构模型\n", "<https://example.com>\n## 结构模型\n")
        (autolink_tight / "THEME.md").write_text(raw_tight, encoding="utf-8")
        tight_err, _ = lint_theme.lint_theme(autolink_tight, schema)
        assert_true(not tight_err, f"自动链接后无空行不应吞掉标题: {tight_err}")

        type7_malformed = Path(tmp) / "type7-malformed-pack"
        write_mini_theme(type7_malformed)
        t7m = (type7_malformed / "THEME.md").read_text(encoding="utf-8")
        t7m = t7m.replace("## 结构模型\n", "<x foo=>\n## 结构模型\n")
        (type7_malformed / "THEME.md").write_text(t7m, encoding="utf-8")
        t7m_err, _ = lint_theme.lint_theme(type7_malformed, schema)
        assert_true(not t7m_err, f"残缺 type-7 标签不应吞掉标题: {t7m_err}")

        type7_dollar = Path(tmp) / "type7-dollar-pack"
        write_mini_theme(type7_dollar)
        t7d = (type7_dollar / "THEME.md").read_text(encoding="utf-8")
        t7d = t7d.replace("## 结构模型\n", "<x $>\n## 结构模型\n")
        (type7_dollar / "THEME.md").write_text(t7d, encoding="utf-8")
        t7d_err, _ = lint_theme.lint_theme(type7_dollar, schema)
        assert_true(not t7d_err, f"非法属性名不应开启 type-7 块: {t7d_err}")

        cdata_case = Path(tmp) / "cdata-case-pack"
        write_mini_theme(cdata_case)
        cdc = (cdata_case / "THEME.md").read_text(encoding="utf-8")
        cdc = cdc.replace("## 结构模型\n", "<![cdata[\n## 结构模型\n]]>\n")
        (cdata_case / "THEME.md").write_text(cdc, encoding="utf-8")
        cdc_err, _ = lint_theme.lint_theme(cdata_case, schema)
        assert_true(not cdc_err, f"小写 cdata 不应按 type-5 HTML 块吞掉标题: {cdc_err}")

        type1_spaced = Path(tmp) / "type1-spaced-pack"
        write_mini_theme(type1_spaced)
        t1s = (type1_spaced / "THEME.md").read_text(encoding="utf-8")
        t1s = t1s.replace("## 结构模型\n", "<script>\n</script >\n## 结构模型\n")
        (type1_spaced / "THEME.md").write_text(t1s, encoding="utf-8")
        t1s_err, _ = lint_theme.lint_theme(type1_spaced, schema)
        assert_true(
            any("结构模型" in e for e in t1s_err),
            f"</script > 不应结束 type-1 块: {t1s_err}",
        )

        type4_lower = Path(tmp) / "type4-lower-pack"
        write_mini_theme(type4_lower)
        t4l = (type4_lower / "THEME.md").read_text(encoding="utf-8")
        t4l = t4l.replace("## 结构模型\n", "<!foo\n## 结构模型\n>\n")
        (type4_lower / "THEME.md").write_text(t4l, encoding="utf-8")
        t4l_err, _ = lint_theme.lint_theme(type4_lower, schema)
        assert_true(not t4l_err, f"小写 <!foo 不应按 type-4 吞掉标题: {t4l_err}")

        type7_in_para = Path(tmp) / "type7-in-para-pack"
        write_mini_theme(type7_in_para)
        t7p = (type7_in_para / "THEME.md").read_text(encoding="utf-8")
        t7p = t7p.replace("## 结构模型\n", "前言文字\n<x>\n## 结构模型\n")
        (type7_in_para / "THEME.md").write_text(t7p, encoding="utf-8")
        t7p_err, _ = lint_theme.lint_theme(type7_in_para, schema)
        assert_true(not t7p_err, f"段落中的 type-7 标签不应吞掉后续标题: {t7p_err}")

        lazy_indent = Path(tmp) / "lazy-indent-pack"
        write_mini_theme(lazy_indent)
        liz = (lazy_indent / "THEME.md").read_text(encoding="utf-8")
        liz = liz.replace("## 结构模型\n", "前言文字\n    continuation\n<x>\n## 结构模型\n")
        (lazy_indent / "THEME.md").write_text(liz, encoding="utf-8")
        liz_err, _ = lint_theme.lint_theme(lazy_indent, schema)
        assert_true(not liz_err, f"段落缩进续行后的 type-7 不应吞掉标题: {liz_err}")

        setext_type7 = Path(tmp) / "setext-type7-pack"
        write_mini_theme(setext_type7)
        stx = (setext_type7 / "THEME.md").read_text(encoding="utf-8")
        stx = stx.replace("## 结构模型\n", "前言\n=====\n<x>\n## 结构模型\n")
        (setext_type7 / "THEME.md").write_text(stx, encoding="utf-8")
        stx_err, _ = lint_theme.lint_theme(setext_type7, schema)
        assert_true(
            any("结构模型" in e for e in stx_err),
            f"setext 后的 type-7 应吞掉后续标题: {stx_err}",
        )

        spaced_thematic = Path(tmp) / "spaced-thematic-pack"
        write_mini_theme(spaced_thematic)
        sth = (spaced_thematic / "THEME.md").read_text(encoding="utf-8")
        sth = sth.replace("## 结构模型\n", "前言文字\n_ _ _\n<x>\n## 结构模型\n")
        (spaced_thematic / "THEME.md").write_text(sth, encoding="utf-8")
        sth_err, _ = lint_theme.lint_theme(spaced_thematic, schema)
        assert_true(
            any("结构模型" in e for e in sth_err),
            f"_ _ _ 主题分隔后 type-7 应吞掉后续标题: {sth_err}",
        )

        tab_indent_code = Path(tmp) / "tab-indent-code-pack"
        write_mini_theme(tab_indent_code)
        tic = (tab_indent_code / "THEME.md").read_text(encoding="utf-8")
        tic = tic.replace("## 结构模型\n", "\tcode\n<x>\n## 结构模型\n")
        (tab_indent_code / "THEME.md").write_text(tic, encoding="utf-8")
        tic_err, _ = lint_theme.lint_theme(tab_indent_code, schema)
        assert_true(
            any("结构模型" in e for e in tic_err),
            f"tab 缩进代码后 type-7 应吞掉后续标题: {tic_err}",
        )

        type1_selfclose = Path(tmp) / "type1-selfclose-pack"
        write_mini_theme(type1_selfclose)
        t1sc = (type1_selfclose / "THEME.md").read_text(encoding="utf-8")
        t1sc = t1sc.replace("## 结构模型\n", "<script/>\n\n## 结构模型\n")
        (type1_selfclose / "THEME.md").write_text(t1sc, encoding="utf-8")
        t1sc_err, _ = lint_theme.lint_theme(type1_selfclose, schema)
        assert_true(not t1sc_err, f"<script/> 不应按 type-1 吞到文件末尾: {t1sc_err}")

        search_block = Path(tmp) / "search-block-pack"
        write_mini_theme(search_block)
        seb = (search_block / "THEME.md").read_text(encoding="utf-8")
        seb = seb.replace("## 结构模型\n", "<search foo=>\n## 结构模型\n")
        (search_block / "THEME.md").write_text(seb, encoding="utf-8")
        seb_err, _ = lint_theme.lint_theme(search_block, schema)
        assert_true(
            any("结构模型" in e for e in seb_err),
            f"<search foo=> 应按 type-6 吞掉标题: {seb_err}",
        )

        html_slot_heading = Path(tmp) / "html-slot-heading-pack"
        write_mini_theme(html_slot_heading)
        hsh = (html_slot_heading / "THEME.md").read_text(encoding="utf-8")
        hsh = hsh.replace(
            "## 文章骨架\n",
            "<div>\n### slot:bogus\n</div>\n\n## 文章骨架\n",
        )
        (html_slot_heading / "THEME.md").write_text(hsh, encoding="utf-8")
        hsh_err, _ = lint_theme.lint_theme(html_slot_heading, schema)
        assert_true(
            not any("slot:bogus" in e for e in hsh_err),
            f"HTML 块里的 ### slot: 不应当成组件标题: {hsh_err}",
        )

        dup_visible_slot = Path(tmp) / "dup-visible-slot-pack"
        write_mini_theme(dup_visible_slot)
        dvs = (dup_visible_slot / "THEME.md").read_text(encoding="utf-8")
        dvs = dvs.replace("### slot:hero\n", "<div>\n### slot:root\n</div>\n\n### slot:hero\n")
        (dup_visible_slot / "THEME.md").write_text(dvs, encoding="utf-8")
        dvs_err, _ = lint_theme.lint_theme(dup_visible_slot, schema)
        assert_true(
            not any("slot:root" in e and "html" in e for e in dvs_err),
            f"HTML 块里重复的 ### slot:root 不应另建组件区域: {dvs_err}",
        )

        type1_mismatch = Path(tmp) / "type1-mismatch-pack"
        write_mini_theme(type1_mismatch)
        t1m = (type1_mismatch / "THEME.md").read_text(encoding="utf-8")
        t1m = t1m.replace("## 结构模型\n", "<script></style></script>\n## 结构模型\n")
        (type1_mismatch / "THEME.md").write_text(t1m, encoding="utf-8")
        t1m_err, _ = lint_theme.lint_theme(type1_mismatch, schema)
        assert_true(not t1m_err, f"同行匹配的 </script> 应结束 type-1 块: {t1m_err}")

        selfclose_md = Path(tmp) / "selfclose-md-pack"
        write_mini_theme(selfclose_md)
        raw_sc = (selfclose_md / "THEME.md").read_text(encoding="utf-8")
        (selfclose_md / "THEME.md").write_text(f"<span/>\n\n{raw_sc}", encoding="utf-8")
        sc_md_err, _ = lint_theme.lint_theme(selfclose_md, schema)
        assert_true(not sc_md_err, f"自闭合 <span/> 不应吞掉后续结构: {sc_md_err}")

        mixed_fence = Path(tmp) / "mixed-fence-pack"
        write_mini_theme(mixed_fence)
        mf = (mixed_fence / "THEME.md").read_text(encoding="utf-8")
        mf = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```~html\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```~\n",
            mf,
            count=1,
            flags=re.S,
        )
        (mixed_fence / "THEME.md").write_text(mf, encoding="utf-8")
        mf_err, _ = lint_theme.lint_theme(mixed_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in mf_err),
            f"混合字符围栏不应算作 html 实现: {mf_err}",
        )

        tick_info_fence = Path(tmp) / "tick-info-fence-pack"
        write_mini_theme(tick_info_fence)
        tif = (tick_info_fence / "THEME.md").read_text(encoding="utf-8")
        tif = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```html `example`\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```\n",
            tif,
            count=1,
            flags=re.S,
        )
        (tick_info_fence / "THEME.md").write_text(tif, encoding="utf-8")
        tif_err, _ = lint_theme.lint_theme(tick_info_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in tif_err),
            f"反引号围栏 info 含反引号不应算实现: {tif_err}",
        )

        type1_fence = Path(tmp) / "type1-fence-pack"
        write_mini_theme(type1_fence)
        t1 = (type1_fence / "THEME.md").read_text(encoding="utf-8")
        t1 = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n<script>\n```html\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```\n</script>\n",
            t1,
            count=1,
            flags=re.S,
        )
        (type1_fence / "THEME.md").write_text(t1, encoding="utf-8")
        t1_err, _ = lint_theme.lint_theme(type1_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in t1_err),
            f"script/pre 等 type-1 HTML 块里的围栏不应算实现: {t1_err}",
        )

        pi_fence = Path(tmp) / "pi-fence-pack"
        write_mini_theme(pi_fence)
        pif = (pi_fence / "THEME.md").read_text(encoding="utf-8")
        pif = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n<?xml\n```html\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```\n?>\n",
            pif,
            count=1,
            flags=re.S,
        )
        (pi_fence / "THEME.md").write_text(pif, encoding="utf-8")
        pif_err, _ = lint_theme.lint_theme(pi_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in pif_err),
            f"处理指令块里的围栏不应算实现: {pif_err}",
        )

        type7_quote_fence = Path(tmp) / "type7-quote-fence-pack"
        write_mini_theme(type7_quote_fence)
        t7 = (type7_quote_fence / "THEME.md").read_text(encoding="utf-8")
        t7 = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n<x-foo title=\">\">\n```html\n<p style=\"font-size:16px;\"><span leaf=\"\">页脚</span></p>\n```\n",
            t7,
            count=1,
            flags=re.S,
        )
        (type7_quote_fence / "THEME.md").write_text(t7, encoding="utf-8")
        t7_err, _ = lint_theme.lint_theme(type7_quote_fence, schema)
        assert_true(
            any("slot:footer" in e and "html" in e for e in t7_err),
            f"type-7 引号内 > 后的围栏不应算实现: {t7_err}",
        )

        table_foster_comp = lint_theme.lint_html_block(
            '<table style="width:100%;"><span leaf="">'
            '<tr style="font-size:16px;"><td style="font-size:16px;">中文。</td></tr></table>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg or "未包" in msg for _, msg in table_foster_comp),
            f"组件 table 清栈后中文应失败: {table_foster_comp}",
        )

        escape_comp = lint_theme.lint_html_block(
            '<p style="pos\\69 tion:fixed;margin:0;font-size:16px;"><span leaf="">{{footer}}</span></p>',
            "### slot:footer",
        )
        assert_true(
            any("position" in msg.lower() or "fixed" in msg.lower() for _, msg in escape_comp),
            f"组件 CSS 转义 position:fixed 应失败: {escape_comp}",
        )

        leaf_block_comp = lint_theme.lint_html_block(
            '<span leaf=""><p style="margin:0">中文。</p></span>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg and "块" in msg for _, msg in leaf_block_comp),
            f"组件 leaf 内块级标签应失败: {leaf_block_comp}",
        )

        leaf_quote_comp = lint_theme.lint_html_block(
            '<span leaf=""><blockquote style="margin:0">中文。</blockquote></span>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg and "块" in msg for _, msg in leaf_quote_comp),
            f"组件 leaf 内 blockquote 应失败: {leaf_quote_comp}",
        )

        select_comp = lint_theme.lint_html_block(
            '<select><option><span leaf="">中文。</span></option></select>',
            "### slot:footer",
        )
        assert_true(
            any("select" in msg.lower() or "option" in msg.lower() for _, msg in select_comp),
            f"组件 <select> 应失败: {select_comp}",
        )

        dialog_comp = lint_theme.lint_html_block(
            '<dialog style="margin:0;font-size:16px;"><p style="margin:0;font-size:16px;">'
            '<span leaf="">中文。</span></p></dialog>',
            "### slot:footer",
        )
        assert_true(
            any("dialog" in msg.lower() or "details" in msg.lower() or "noscript" in msg.lower() for _, msg in dialog_comp),
            f"组件 <dialog> 应失败: {dialog_comp}",
        )

        details_comp = lint_theme.lint_html_block(
            '<details style="margin:0;font-size:16px;"><summary style="font-size:16px;">'
            '<span leaf="">中文。</span></summary></details>',
            "### slot:footer",
        )
        assert_true(
            any("dialog" in msg.lower() or "details" in msg.lower() or "noscript" in msg.lower() for _, msg in details_comp),
            f"组件 <details> 应失败: {details_comp}",
        )

        noscript_comp = lint_theme.lint_html_block(
            '<noscript><p style="margin:0;font-size:16px;"><span leaf="">{{footer}}</span></p></noscript>',
            "### slot:footer",
        )
        assert_true(
            any("dialog" in msg.lower() or "details" in msg.lower() or "noscript" in msg.lower() for _, msg in noscript_comp),
            f"组件 <noscript> 应失败: {noscript_comp}",
        )

        doc_comp = lint_theme.lint_html_block(
            '<html><body><p style="margin:0"><span leaf="">中文。</span></p></body></html>',
            "### slot:footer",
        )
        assert_true(
            any("html" in msg.lower() or "body" in msg.lower() for _, msg in doc_comp),
            f"组件文档壳 html/body 应失败: {doc_comp}",
        )

        li_quote_comp = lint_theme.lint_html_block(
            '<ul style="margin:0;"><li style="margin:0;font-size:16px;">'
            '<blockquote style="margin:0;font-size:16px;"><span leaf="">一。'
            '<li style="margin:0;font-size:16px;">二。</li></ul>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg or "未包" in msg for _, msg in li_quote_comp),
            f"组件 blockquote 内省略 </li> 应失败: {li_quote_comp}",
        )

        nested_a_comp = lint_theme.lint_html_block(
            '<p style="margin:0;font-size:16px;"><a><span leaf="">一。<a>二。</a></span></a></p>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg or "未包" in msg for _, msg in nested_a_comp),
            f"组件嵌套 a 清栈后中文应失败: {nested_a_comp}",
        )

        p_then_li_comp = lint_theme.lint_html_block(
            '<ul style="margin:0;"><p style="margin:0;font-size:16px;"><span leaf="">一。'
            '<li style="margin:0;font-size:16px;">二。</li></ul>',
            "### slot:footer",
        )
        assert_true(
            any("leaf" in msg or "未包" in msg for _, msg in p_then_li_comp),
            f"组件 li 隐含闭合 p 后中文应失败: {p_then_li_comp}",
        )

        link_comp = lint_theme.lint_html_block(
            '<link rel="stylesheet" href="https://example.test/theme.css">'
            '<p style="margin:0;font-size:16px;"><span leaf="">{{footer}}</span></p>',
            "### slot:footer",
        )
        assert_true(
            any("link" in msg.lower() or "禁止" in msg for _, msg in link_comp),
            f"组件里的 <link> 应失败: {link_comp}",
        )

        unstyled_comp = Path(tmp) / "unstyled-comp-pack"
        write_mini_theme(unstyled_comp)
        uc = (unstyled_comp / "THEME.md").read_text(encoding="utf-8")
        uc = re.sub(
            r"### slot:footer\n\n```html\n.*?```\n",
            "### slot:footer\n\n```html\n<p><span leaf=\"\">{{footer}}</span></p>\n```\n",
            uc,
            count=1,
            flags=re.S,
        )
        (unstyled_comp / "THEME.md").write_text(uc, encoding="utf-8")
        uc_err, _ = lint_theme.lint_theme(unstyled_comp, schema)
        assert_true(
            any("style" in e.lower() and "footer" in e for e in uc_err),
            f"组件缺少 inline style 应失败: {uc_err}",
        )

        h4_comp = lint_theme.lint_html_block(
            '<h4><span leaf="">中文。</span></h4>',
            "### slot:footer",
        )
        assert_true(
            any("style" in msg.lower() and ("h4" in msg.lower() or "缺少" in msg) for _, msg in h4_comp),
            f"组件无 style 的 h4 应失败: {h4_comp}",
        )

        mismatch_h_comp = lint_theme.lint_html_block(
            '<h1 style="font-size:22px;margin:0;"><span leaf="">一。</h2>二。</span></h1>',
            "### slot:footer",
        )
        assert_true(
            any("包裹" in msg or "leaf" in msg.lower() for _, msg in mismatch_h_comp),
            f"主题 HTML 中 </h2> 应闭合 h1: {mismatch_h_comp}",
        )

        stray_p_comp = lint_theme.lint_html_block(
            '<p style="margin:0;font-size:16px;"><span leaf="">{{footer}}</span></p></p>',
            "### slot:footer",
        )
        assert_true(
            any("style" in msg.lower() and ("p" in msg.lower() or "缺少" in msg) for _, msg in stray_p_comp),
            f"游离 </p> 插入的空段落应缺 style: {stray_p_comp}",
        )

        unstyled_article_comp = lint_theme.lint_html_block(
            '<article><span leaf="">中文。</span></article>',
            "### slot:footer",
        )
        assert_true(
            any("style" in msg.lower() and ("article" in msg.lower() or "缺少" in msg) for _, msg in unstyled_article_comp),
            f"组件无 style 的 article 应失败: {unstyled_article_comp}",
        )

        hyphen_ph = lint_theme.lint_html_block(
            '<p style="margin:0">{{author-name}}</p>',
            "### sig:author-name",
        )
        assert_true(
            any("占位" in msg or "author-name" in msg for _, msg in hyphen_ph),
            f"带连字符的占位符未包 leaf 应失败: {hyphen_ph}",
        )

        spaced_ph = lint_theme.lint_html_block(
            '<p style="margin:0">{{ body }}</p>',
            "### slot:footer",
        )
        assert_true(
            any("占位" in msg or "leaf" in msg for _, msg in spaced_ph),
            f"带空格的占位符未包 leaf 应失败: {spaced_ph}",
        )

        dotted_ph = lint_theme.lint_html_block(
            '<p style="margin:0">{{body.name}}</p>',
            "### slot:footer",
        )
        assert_true(
            any("占位" in msg or "leaf" in msg for _, msg in dotted_ph),
            f"带点号的占位符未包 leaf 应失败: {dotted_ph}",
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
