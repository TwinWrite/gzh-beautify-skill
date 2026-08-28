# 工厂冒烟示例

这些主题包用来对照结构模型和气质表，证明工厂能产出完整三件套。**不是**官方默认货架。

渲染发现只看 `themes/{id}/`（以及用户给出的路径）。这里的目录不会被自动选中。新气质仍应重新走工厂，不要复制这些 HTML 换皮。

| id | 中文名 | 结构模型 | 气质对照 |
|----|--------|----------|----------|
| `mist-masthead` | 雾蓝刊头 | narrative / sparse / masthead / hairline / long-breath | 杂志刊头、细线、衬线 |
| `step-workshop` | 步骤工坊 | explainer / packed / numbered-chapter / soft-card / staccato | 教程绿卡、编号、清单 |
| `paper-journal` | 纸页手记 | journal / balanced / labeled-rail / paper / documentary | 内刊手记、左轨、摘录 |
| `cinnabar-catalog` | 朱印目录 | catalog / packed / stamp / ink / staccato | 票据戳记、条目、盘点 |
| `graphite-editorial` | 石墨刊读 | narrative / sparse / masthead / hairline / long-breath | 石墨极简、超大编号、几乎无色块 |
| `moss-zen` | 苔色留白 | journal / sparse / masthead / paper / long-breath | 禅意留白、居中衬线、1px 细线 |

「观点正红」走 `narrative` + `numbered-chapter` + 正红 brand，不必另内置一套；现有朱印目录覆盖的是戳记/盘点，不是红白评论。

对照外部精致公众号风格时：只抽色、留白、线、密度、情绪，写进 `theme.json` 再生成自己的签名槽。禁止复刻对方组件 HTML、文案或 Logo。
