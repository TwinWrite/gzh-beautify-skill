# 用主题包渲染 Markdown

本文件是**第二工作流**。前提：磁盘上已经有一套通过 `lint_theme.py` 的主题包。没有主题包就转到 [theme-factory.md](theme-factory.md)，不要在渲染时即兴写一套一次性 HTML。

## 定位主题包

按顺序找 `theme.json` + `THEME.md`：

1. 用户给出的目录
2. `./themes/{id}/`
3. `<SKILL_ROOT>/themes/{id}/`

用户只给了中文名：在上述 `themes/` 里打开各包 `theme.json` 的 `name` 匹配。匹配不到就列出已有 id，问清楚。一个工作目录有多套主题、用户没指定：问要用哪套，**不要默认第一套**。

一次渲染只用一个主题包。不要跨包借槽。

## 步骤

```
渲染：
- [ ] 1. Read 主题包 THEME.md + theme.json
- [ ] 2. 解析 Markdown（缺格式先归一成 md）
- [ ] 3. 判定文章类型，查配方
- [ ] 4. 按骨架填槽，不手写新组件
- [ ] 5. 写入干净正文 HTML
- [ ] 6. validate_article.py --strict 到 0 ERROR / 0 WARN
- [ ] 7. wrap_preview.py 生成预览页
```

### 输入归一

用户可能给 `.md`、纯文本、`.docx`、网页富文本。非 Markdown 先转成 Markdown 草稿再排。不要在转换阶段美化语气或增删论点。

docx 可用 python-docx（若环境没有就声明并请用户另存 md / 粘贴文本）。PDF 按页读出后清页眉页脚再结构化。

用户说「直接排 / 一键 / 不用问」：不追问结构，但**主题包仍必须存在**；没有主题就先走工厂（可把 brief 从文章气质推断）再排，并在交付时说明用了哪套、为何生产它。

### 结构解析

| 元素 | 规则 |
|------|------|
| 标题 | `#` 或 frontmatter `title` → `hero` |
| 开头引言 | 文首 `>` → 可进 `hero` 副题或 `quote_pull`，以主题映射表为准 |
| 章节 | `##` → `h2`，按出现顺序 `01` `02`… |
| 小节 | `###` → `h3` 或配方指定的 `h3_label` |
| 加粗 / 高亮 / 下划线 / 删除线 | `**` / `==` / `++` 或双下划线 / `~~` |
| 其它引用 | `>` → `blockquote` 或 `quote_pull` |
| 图 / GIF | `![]()` ；空 alt 不编造说明 |
| 代码 | 围栏 → `code_dark` 或 `code_light`（看主题 surface/voice）；行内 → `code_inline` |
| 列表 / 表 / 分割线 | `ul` `ol` `table` `divider` |
| 待补 | `【插入…】` → `media_ph` |

文章类型（取主导）：步骤命令多 → `tutorial`；并列条目多 → `listicle`；论证多 → `opinion`；人物引语多 → `interview`；数字对比多 → `report`；随笔 → `essay`；案例过程 → `case`。

### 装配铁律

- HTML **只从 THEME.md 的槽复制**，改占位符，不现场发明新 markup。
- 行内槽嵌进 `paragraph` 的 `{{body}}`。
- 每个正文段落主动用 `underline` 标 1–3 个 4–15 字的关键短语（核心观点、数据、专名）。没有加粗也要标；没有要点的段落可以不标。
- 章节英文标签按标题语义生成（实测→TEST、教程→TUTORIAL、总结→SUMMARY），主题 `h2` 有 `{{en_label}}` 才填。
- 末章若是结语且主题规定了编号变体（如 `∞`），只用于最后一章。
- `toc` 只放 3 个看点，不是全文章节表。
- `footer` 全文只出现一次。原文已有「我是某某」或三连 CTA，并入 footer，不要叠两份。
- 用户没留作者：保留 `{{author}}` / `{{bio}}` 并在交付时提醒替换。
- 不要输出 `<html>` `<head>` `<body>`：干净文件从 `slot:root` 的 `<section>` 开始。
- 中文标点在生成时就写全角，不要事后批量替换（以免误伤代码）。

### 输出

干净正文：

```
{原文件名}_排版_{中文名}({id}).html
```

预览：

```bash
python3 <SKILL_ROOT>/scripts/wrap_preview.py <干净正文.html>
```

告知用户：打开 `*_预览.html` → 点复制 → 到公众号编辑器粘贴。校验结论一并附上。

## 智能处理清单（渲染时必须做）

1. `##` 连续编号
2. 英文标签
3. 逐段关键词下划线
4. 引言里的核心词用 `mark` 或 `strong`（按映射表）
5. 目录三看点
6. 签名占位或沿用原文署名
7. 列表按映射转；没有更合适的签名槽就用 `ul`/`ol`
8. 全文全角标点（代码除外）
