# gzh-beautify-skill · 公众号排版主题工厂

**生产可复用的微信公众号排版主题包，再用主题包把 Markdown 转成可粘贴的内联 HTML。**

本 skill **不提供预设主题目录**。没有主题时先生产主题；有主题后，渲染只填槽、不即兴写样式。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 和「主题超市」的差别

常见做法是：仓库里预置若干套风格，排版时从中挑选，不够再生成一套附到目录末尾。

这里反过来：

1. **主题包是主产物**（`theme.json` + `THEME.md` + `preview.html`）
2. **26 个必选槽是封闭契约**，保证任意 Markdown 都能填进去
3. **签名槽才表达个性**（刊头、步骤条、手记栏……由结构模型推导，而不是换皮）
4. **渲染是第二工作流**：只读已入库主题包，不再现场发明 HTML

公众号编辑器会清洗外链 CSS、剥 `id`、丢掉不在白名单里的样式。主题因此不是 CSS 文件，而是每个标签都带齐 inline `style`、中文包在 `span[leaf]` 里的槽位库。约束见 [`references/wechat-constraints.md`](references/wechat-constraints.md)。

## 快速开始

```bash
npx skills add https://github.com/TwinWrite/gzh-beautify-skill
```

或把本仓库 clone 到 Agent 的 skills 目录。装好后直接说：

> 按「雾蓝杂志、细线分隔、衬线标题」的气质，生成一套公众号排版主题

Agent 会写入：

```
themes/{id}/
  theme.json      # 结构模型 + 九色 + 字体
  preview.html    # 整页看气质
  THEME.md        # 槽位 HTML + 骨架 + 配方 + 映射
```

确认预览后，再：

> 用 `{id}` 把 `article.md` 转成公众号 HTML

得到干净正文和带「复制到公众号」按钮的预览页。

## 工作流

### 生产主题

1. 一次收齐 brief（描述或参考图必填，色/字体可空）
2. 推导结构模型（叙事/密度/标题体系/表面/节奏）和色板
3. 生成整页 `preview.html`（必选槽 + 签名槽）
4. 确认气质后编译 `THEME.md`
5. `python3 scripts/lint_theme.py themes/{id}` 到 0 ERROR

### 用主题渲染

1. 定位主题包（用户路径 → `./themes/{id}/` → skill 内 `themes/{id}/`）
2. 按 `THEME.md` 填槽：章节编号、逐段关键词下划线、全角标点、唯一文末签名
3. `python3 scripts/validate_article.py --strict <正文.html>`
4. `python3 scripts/wrap_preview.py <正文.html>`

没有主题包就先生产，不要手写一次性样式充数。

## 脚本

```bash
python3 scripts/selftest.py
python3 scripts/lint_theme.py themes              # 空目录也通过
python3 scripts/validate_article.py --strict out.html
python3 scripts/wrap_preview.py out.html
```

- **源头关** `lint_theme.py`：json 契约、对比度、缺槽、禁用 HTML
- **产物关** `validate_article.py`：平台红线、`span[leaf]`、半角标点

## 目录

```
gzh-beautify-skill/
├── SKILL.md
├── references/          # 约束、契约、工厂、渲染合同
├── scripts/             # 校验与预览
├── assets/              # 预览壳、试排稿
└── themes/              # 生产输出（默认空）
```

## License

MIT © 2026 TwinWrite
