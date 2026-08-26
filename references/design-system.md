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
