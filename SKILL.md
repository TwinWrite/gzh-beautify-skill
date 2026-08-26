---
name: gzh-beautify
description: 生产可复用的微信公众号排版主题包，并用已生成的主题包把 Markdown 转成可粘贴进公众号编辑器的内联 HTML。不提供预设主题目录；没有主题时先生产主题。适用于用户提到公众号排版、生成排版主题、自定义风格、参考图做主题、Markdown 转公众号 HTML、微信排版、gzh 主题工厂。不用于普通网页、落地页或 PPT。
---

# 公众号排版主题工厂

本 skill 的产品是**主题包**，不是主题货架。先按气质生产一套槽位完整的主题，再拿这套主题把 Markdown 填进槽里，得到可粘贴进微信公众号编辑器的 HTML。

仓库里默认**没有**可选主题。禁止为了「先排一版」而手写未入库的一次性样式。

```
生产主题（主） → themes/{id}/{theme.json, THEME.md, preview.html}
用主题渲染（辅） → 干净正文.html + 预览.html
```

细节按需再读，不要把参考文档一次性全读进上下文：

- 平台红线：[references/wechat-constraints.md](references/wechat-constraints.md)
- 结构模型与色板：[references/design-system.md](references/design-system.md)
- 目录与槽位契约：[references/theme-schema.md](references/theme-schema.md)
- 生产步骤与提示词：[references/theme-factory.md](references/theme-factory.md)
- Markdown 怎么填槽：[references/render-contract.md](references/render-contract.md)

## 分流

| 用户意图 | 去做 |
|----------|------|
| 生成 / 定制主题、按参考图做风格、还没有主题包 | 读 `theme-factory.md`，走生产 |
| 已有主题包，把 md/docx/文本转公众号 HTML | 读 `render-contract.md`，走渲染 |
| 「排这篇」但找不到主题包 | 先生产（brief 可从文章气质推断），再渲染，交付时说明主题从何而来 |
| 普通网页、落地页、PPT | 不用本 skill |

主题包查找顺序：用户路径 → `./themes/{id}/` → `<SKILL_ROOT>/themes/{id}/`。

## 生产主题

```
- [ ] 收 brief（描述或参考图必有，其余可补全）
- [ ] 写 theme.json（结构模型 + 九色 + 字体）
- [ ] 写 preview.html（26 必选槽 + 8–16 签名槽，整页预览）
- [ ] 用户确认气质后再编译 THEME.md
- [ ] python3 <SKILL_ROOT>/scripts/lint_theme.py <主题目录>
- [ ] （推荐）试排 assets/sample-article.md 并 validate --strict
```

约束摘要（完整清单以 wechat-constraints 为准）：

- 可粘贴 HTML：`section/p/span` + 全内联 style + 中文包在 `<span leaf="">` 里
- 禁 `div/class/id/style标签/grid/position/CSS变量`
- 代码行用多个 `p`，不用 `white-space:pre`
- 字号 ≤ 24px；根宽 677px
- 强调用竖条/标签/下划线，四周虚线框只给待补素材

`THEME.md` 必须含固定七章：结构模型、设计变量、必选槽、签名槽、文章骨架、文章类型配方、Markdown 映射。每个必选槽标题为 `### slot:{id}`。

## 用主题渲染

```
- [ ] 读该包 THEME.md，按槽复制 HTML，不即兴写新组件
- [ ] 解析 md：标题/章节/行内标记/代码/图/列表/表
- [ ] 按配方选签名槽；章节编号；每段 1–3 个下划线关键词
- [ ] 正文全角标点（代码除外）；footer 全文一处
- [ ] 产物从 root 的 section 起，不要 html/head/body
- [ ] python3 <SKILL_ROOT>/scripts/validate_article.py --strict <正文.html>
- [ ] python3 <SKILL_ROOT>/scripts/wrap_preview.py <正文.html>
```

文件名：`{原名}_排版_{中文名}({id}).html`。交付预览页路径 + 干净正文兜底路径 + 校验结果。

## 脚本

```bash
python3 <SKILL_ROOT>/scripts/lint_theme.py <主题目录或 themes/>
python3 <SKILL_ROOT>/scripts/validate_article.py --strict <正文.html>
python3 <SKILL_ROOT>/scripts/wrap_preview.py <正文.html>
python3 <SKILL_ROOT>/scripts/selftest.py
```

`wrap_preview.py` 的工具条只存在于预览外壳，不进入被复制的正文。

## 不要做

- 不要内置或推荐一套「官方默认主题」充数
- 不要把预览页拿去跑 `validate_article.py`
- 不要跨主题混槽
- 不要代写文章；本 skill 只生产主题和排版
- 不要输出普通网站 CSS/JS 组件冒充公众号正文
