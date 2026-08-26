# 主题工厂

用户要的是**生产一套可复用主题**，不是从目录里挑。读完 [wechat-constraints.md](wechat-constraints.md)、[design-system.md](design-system.md)、[theme-schema.md](theme-schema.md) 再执行。

## 触发

- 生成 / 定制 / 设计一套公众号排版主题
- 按描述、品牌色、参考图做组件库
- 现有主题不满意，要新风格
- 仓库里还没有主题包，但用户已经在谈排版（先生产，再渲染）

## 步骤

复制清单并勾选：

```
主题生产：
- [ ] 1. 收 brief（一次问全）
- [ ] 2. 推导结构模型 + 色板，写入 theme.json
- [ ] 3. 生成 preview.html（必选槽 + 签名槽）
- [ ] 4. 用户整页确认气质
- [ ] 5. 编译 THEME.md（补 leaf、骨架、配方、映射）
- [ ] 6. lint_theme.py 0 ERROR
- [ ] 7. 可选：用 sample-article.md 试排并 validate_article.py --strict
- [ ] 8. 交付目录路径与使用方式
```

### 1. 收 brief

只强制「气质描述」或参考图。其余空着就按设计系统补全。一次问完，不要逐项追问。

| 字段 | 空值时 |
|------|--------|
| 中文名 / id | 从气质生成 |
| 描述 / 参考图 | 至少要有一个 |
| 品牌色 / 纸色 / 正文色 / 点睛色 | 从描述或图片推导 |
| 字体 stack | 按气质从五档里选 |
| 圆角 / 阴影 | 按 `surface` 定 |
| 适用场景 | 写成 `tags.scenes` |

参考图只提取视觉特征（色、留白、线、密度、情绪），禁止复刻可识别商标、人物、整页构图或原文案。文字 brief 与图片冲突时，以用户写明的文字为准。

id 冲突：问覆盖还是换名。覆盖前保留旧目录内容的 diff 意识，不要静默删。

### 2. 写 theme.json

先在内部完成结构模型判断，再填 tokens。然后写入：

```
<输出根>/themes/{id}/theme.json
```

输出根：用户指定目录 > 当前工作目录 > skill 根目录。默认写当前工作目录的 `themes/`，方便主题跟着项目走；用户明确要求「写进 skill」才写 `<SKILL_ROOT>/themes/`。

`underline_css` 从 `tokens.color.underline` 生成，例如 `border-bottom:2px solid #C5D4E0;font-weight:600;`。

### 3. 生成 preview.html

按文末提示词生成完整预览。全部槽在同一页连续排布，让用户一次看完，不要逐块确认。

保存为 `themes/{id}/preview.html`。

### 4. 确认

请用户用浏览器打开预览。用户说改配色 / 改密度 / 改标题体系：回到第 2–3 步改 json 与预览，不要直接去改未编译的 THEME.md。

### 5. 编译 THEME.md

把预览里的块变成契约槽位：

1. 去掉预览用 `id` / 槽名标注 / 文档外壳。
2. 每个文字节点补 `<span leaf="">`；装饰空节点补 `<span leaf=""><br></span>`。
3. 示意文案换成 `{{placeholder}}`。
4. 写齐七个固定章节。
5. 配方表按 `voice` 填写，不要七种文章类型共用同一组签名槽。

### 6. 校验

```bash
python3 <SKILL_ROOT>/scripts/lint_theme.py <主题目录>
```

ERROR 必须为 0。对比度、缺槽、禁用 HTML 都在这一关。

### 7. 试排（推荐）

用 [render-contract.md](render-contract.md) 把 `assets/sample-article.md` 排成一篇，跑：

```bash
python3 <SKILL_ROOT>/scripts/validate_article.py --strict <试排.html>
```

试排文件不要提交进主题包。

### 8. 交付

告知：中文名、id、目录路径、结构模型一句话、如何用这套主题排文章（「用 `{name}`（`{id}`）把 `article.md` 转成公众号 HTML」）。

## 修改已有主题

改 tokens 就同步 `theme.json` + `preview.html` + `THEME.md` 三处色值，再跑 lint。只改某一个签名槽时，预览里对应块也要改。删主题：删整个目录。

## 生成提示词

收集完 brief、写完 `theme.json` 之后，用下面提示词生成 `preview.html`。把 json 全文贴进提示词。不要套用任何现成主题的骨架。

---

你是微信公众号排版主题的工厂。目标是产出一套**可复用槽位预览页**，不是一篇文章，也不是网站落地页。

输入：用户 brief + 已经定稿的 theme.json（结构模型、九色、字体、圆角阴影都已确定）。你必须服从 json，不得另起一套色。

先根据 `structure_model` 决定签名槽的视觉语法，再画必选槽。必选槽 26 个一个不能少；签名槽 8–16 个，名字要具体，并写进页面注释。

必选槽 id：root, hero, toc, h2, h3, h3_label, paragraph, divider, strong, mark, underline, strike, code_inline, blockquote, callout_tip, callout_warn, quote_pull, ul, ol, table, code_dark, code_light, image, image_gif, media_ph, footer。

预览页要求：

1. 完整 HTML 文档。`<body>` 里每个槽一块，块前用浅灰小字标注 `slot:id` 或 `sig:id`。
2. 预览块可以带 `id="preview-slot-hero"` 这种定位 id；style 仍以内联为主。
3. 根视觉：纸色底、max-width 677px、系统字体栈按 json 的 stack 展开。
4. 占位文案只用结构说明（「主标题占位」「流程节点占位」），不要真实品牌、地名、人名、价格、功能名。
5. 图片用色块 section 模拟，不要外链占位图。
6. 字号 ≤ 24px。不要 grid、不要 CSS 变量、不要 position sticky/fixed/absolute、不要 float、不要 svg/canvas/video/button/form。
7. 代码块演示「每行一个 p」，不要 white-space:pre。
8. 强调用竖条/标签/下划线，不要四周虚线框（media_ph 除外）。
9. 主色只做锚点；大面积是 page + ink 灰阶。
10. 即使 flex 失效，堆叠后仍能读。子项间距用 margin，不靠 gap。

签名槽必须能从 voice/heading/surface 讲出差异：刊头主题不要长成步骤卡片墙；教程主题不要长成全是情绪海报。

只输出 HTML 全文，不要 Markdown 围栏，不要前言。

---
