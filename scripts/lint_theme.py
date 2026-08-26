#!/usr/bin/env python3
"""Lint a produced theme package (theme.json + THEME.md + preview.html)."""

from __future__ import annotations

import json
import re
import sys
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
FONT_SIZE = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", re.I)
FOURSIDE_DASHED = re.compile(r"border\s*:\s*[^;{}]*dashed", re.I)
CENTERED = re.compile(r"text-align\s*:\s*center", re.I)
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,38}[a-z0-9]$")

THEME_HTML_CHECKS = [
    (re.compile(r"</?div[\s>]", re.I), "ERROR", "出现 <div>，请用 <section>"),
    (re.compile(r"\sclass\s*=", re.I), "ERROR", "出现 class（交付组件禁止）"),
    (re.compile(r"\sid\s*=", re.I), "ERROR", "出现 id（THEME.md 组件禁止，预览页可用）"),
    (re.compile(r"<style[\s>]", re.I), "ERROR", "出现 <style>"),
    (re.compile(r"<script[\s>]", re.I), "ERROR", "出现 <script>"),
    (re.compile(r"position\s*:\s*(fixed|absolute|sticky)", re.I), "ERROR", "禁止 position fixed/absolute/sticky"),
    (re.compile(r"display\s*:\s*grid", re.I), "ERROR", "禁止 display:grid"),
    (re.compile(r"var\s*\(\s*--", re.I), "ERROR", "禁止 CSS 变量"),
    (re.compile(r"@(media|keyframes|import)", re.I), "ERROR", "禁止 @media/@keyframes/@import"),
    (re.compile(r"white-space\s*:\s*pre", re.I), "ERROR", "禁止 white-space:pre，代码块请逐行 <p>"),
    (re.compile(r"</?(svg|canvas|video|audio|iframe|form|button|input)\b", re.I), "ERROR", "出现禁止标签"),
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


def lint_html_block(html: str, label: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for rx, level, msg in THEME_HTML_CHECKS:
        if rx.search(html):
            found.append((level, f"{label}: {msg}"))
    for size in FONT_SIZE.findall(html):
        if float(size) > 24:
            found.append(("ERROR", f"{label}: font-size {size}px 超过 24px"))
    if FOURSIDE_DASHED.search(html) and not CENTERED.search(html):
        found.append(("WARN", f"{label}: 四周虚线框，正文强调请改用竖条/标签"))
    if ("{{" in html or re.search(r"[一-鿿]", html)) and "leaf" not in html:
        found.append(("ERROR", f"{label}: 有文案或占位但缺少 span leaf"))
    return found


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

    sigs = data.get("signature_slots") if isinstance(data.get("signature_slots"), list) else []
    if sigs and (len(sigs) < 8 or len(sigs) > 16):
        warnings.append(f"signature_slots 建议 8–16 个，当前 {len(sigs)}")

    if not md_path.is_file():
        errors.append("缺少 THEME.md")
        md_text = ""
    else:
        md_text = md_path.read_text(encoding="utf-8")
        for heading in REQUIRED_MD_HEADINGS:
            if heading not in md_text:
                errors.append(f"THEME.md 缺少章节 {heading}")
        for kind in ARTICLE_TYPES:
            if kind not in md_text:
                warnings.append(f"THEME.md 配方可能未覆盖文章类型 {kind}")

        slot_ids = SLOT_HEADING.findall(md_text)
        for required in REQUIRED_SLOTS:
            if required not in slot_ids:
                errors.append(f"THEME.md 缺少 ### slot:{required}")
        dup = sorted({s for s in slot_ids if slot_ids.count(s) > 1})
        if dup:
            errors.append(f"THEME.md 重复槽: {', '.join(dup)}")

        sig_ids = SIG_HEADING.findall(md_text)
        if len(sig_ids) < 8:
            warnings.append(f"签名槽少于 8 个（{len(sig_ids)}）")
        if len(sig_ids) > 16:
            warnings.append(f"签名槽多于 16 个（{len(sig_ids)}）")
        if sigs and sorted(sigs) != sorted(sig_ids):
            errors.append("theme.json signature_slots 与 THEME.md ### sig:* 不一致")

        for match in HTML_FENCE.finditer(md_text):
            html = match.group(1)
            start = md_text.rfind("### ", 0, match.start())
            label = md_text[start:match.start()].splitlines()[0] if start != -1 else "html"
            for level, msg in lint_html_block(html, label.strip()):
                (errors if level == "ERROR" else warnings).append(msg)

    if not preview_path.is_file():
        errors.append("缺少 preview.html")
    else:
        preview = preview_path.read_text(encoding="utf-8")
        if "<html" not in preview.lower():
            warnings.append("preview.html 不像完整 HTML 文档")
        for slot in REQUIRED_SLOTS:
            if f"slot:{slot}" not in preview and f"preview-slot-{slot}" not in preview:
                warnings.append(f"preview.html 可能未展示 slot:{slot}")

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
