# 主题设计系统

生产主题时先定结构模型和色板，再写 HTML。禁止先套一份「通用杂志模板」再换色。

## 结构模型

五个轴，写进 `theme.json` 的 `structure_model`：

| 轴 | 取值 | 含义 |
|----|------|------|
| `voice` | `narrative` / `explainer` / `catalog` / `journal` / `brand` | 叙事、说明、盘点、手记、品牌 |
| `density` | `sparse` / `balanced` / `packed` | 留白多少、卡片多少 |
| `heading` | `masthead` / `numbered-chapter` / `labeled-rail` / `stamp` | 刊头、编号章节、左轨标签、印章/戳记 |
| `surface` | `paper` / `ink` / `soft-card` / `hairline` | 纸感、墨色块、柔阴影卡、细线 |
| `rhythm` | `long-breath` / `staccato` / `documentary` | 长段落、短卡连发、文献记录 |

由结构模型决定**签名槽**长什么样，而不是决定必选槽缺不缺。必选槽永远齐全；签名槽表达个性。

推导例子（不是目录，是生成时的判断）：

- 深度评论 / 杂志感 → `narrative` + `sparse` + `masthead` + `hairline` + `long-breath`；签名槽偏刊头、编者按、拉页引文。
- 教程 / 工具说明 → `explainer` + `packed` + `numbered-chapter` + `soft-card` + `staccato`；签名槽偏步骤条、参数表、检查清单。
- 内刊 / 复盘 → `journal` + `balanced` + `labeled-rail` + `paper` + `documentary`；签名槽偏栏目标签、摘录框、页码感分隔。

用户要「像某类精致公众号杂志」时，用气质推结构，**不要去抄现成组件库的 HTML / 文案 / Logo**。色板按角色另填一套（brand / brand_soft / accent / 灰阶），不要把参考账号的色值当必须克隆的货架：

| 用户说的气质 | 结构模型 | 色板怎么填 | 签名槽语法 |
|--------------|----------|------------|------------|
| 教程绿卡、信息密度高、杂志封面 | `explainer` / `packed` / `numbered-chapter` / `soft-card` / `staccato` | brand 翠绿或青绿，brand_soft 极浅绿，accent 暖色点睛 | 快讯封面卡、步骤条、参数芯片、检查清单 |
| 观点编辑、正红点睛、编号章节 | `narrative` / `balanced` / `numbered-chapter` / `hairline` / `long-breath` | brand 正红，page 近白，accent 少用 | 引言卡、红编号、签名区，少卡片 |
| 石墨灰、极简、细线、几乎无色块 | `narrative` / `sparse` / `masthead` / `hairline` / `long-breath` | brand 接近 ink_muted 的石墨灰，几乎无彩色 | 超大编号、上下细线引文、几何签名 |
| 禅意留白、衬线金句、1px 细线 | `journal` / `sparse` / `masthead` / `paper` / `long-breath` | brand 苔绿，page 米白，密度 sparse | 大段距、居中衬线引文、少卡片 |
| 票据/门票、硬阴影、编号票根 | `catalog` / `packed` / `stamp` / `ink` / `staccato` | brand 饱和，heading 走 stamp | 票签、计数章、细线撕边感（用细线+圆点，不用四周虚线框套标题） |
| 内刊手记、分节多样、编者按 | `journal` / `balanced` / `labeled-rail` / `paper` / `documentary` | brand 褐或橄榄，surface paper | 栏目标签、摘录框、页码、后记 |

`examples/themes/` 里有按上表产出的冒烟包（雾蓝刊头、步骤工坊、纸页手记、朱印目录、石墨刊读、苔色留白），只供对照结构，不进渲染发现路径。

HTML 色值只能来自 `theme.json` 的九色。深色代码块用 `ink` 底 + `page` 字；警告标签用 `ink`（或对比度达标的 `brand_ink`）写在浅底上，不要用过浅的 `accent` 当 12px 标题色。`lint_theme.py` 会拒绝组件 HTML 里未登记的 `#RRGGBB`。

`image` / `image_gif`：`{{src}}` 和 `{{alt}}` 只写在 `<img>` 属性里，`{{caption}}` 只出现在图注；空 alt 不要编造说明。

## 色板角色

九个色值，全部 `#RRGGBB`：

| token | 用途 |
|-------|------|
| `page` | 根底，默认白或近白 |
| `ink` | 标题和正文 |
| `ink_muted` | 说明、图注、弱信息 |
| `brand` | 编号、竖条、少量锚点 |
| `brand_soft` | 浅底卡片、提示块背景 |
| `brand_ink` | 浅底上的标题字 |
| `accent` | 高亮/点睛，与 brand 冷暖对比，全文少用 |
| `rule` | 分割线、浅边框 |
| `underline` | 关键词下划线，比 brand 更浅 |

对比度（相对亮度，见 `scripts/lint_theme.py`）：

- `ink` 在 `page` 上 ≥ 7.0（正文）
- `ink_muted` 在 `page` 上 ≥ 4.5
- `brand_ink` 在 `brand_soft` 上 ≥ 4.5
- 深底签名块如果出现，块内文字对自己的底同样要达标

未声明深色氛围时，`page` 必须是白或近白（相对亮度 ≥ 0.92）。不要把整套主题铺成深色网站。

## 三层强调

| 层 | 频率 | 手段 |
|----|------|------|
| 锚点 | 全文 ≤ 5 处 | brand 加粗、深底浅字、封面点睛 |
| 标记 | 每段 1–3 个短语 | `underline` 槽，4–15 字 |
| 容器 | 按需 | 引用、提示、金句、卡片 |

一段里高亮手法不超过两种。到处加粗等于没有重点。

## 签名槽怎么长

必选槽解决 Markdown 全覆盖；签名槽 8–16 个，命名必须具体（「刊头摘要」而不是「卡片」）。签名槽可以没有 Markdown 对应，只在配方表里按文章类型选用。

禁止：把另一套主题的签名槽换色复用。签名槽必须能从本次结构模型说清楚来源。
