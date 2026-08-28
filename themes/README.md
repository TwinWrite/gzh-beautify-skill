# 主题包目录

这里存放**生产出来的主题包**，不是预设主题超市。

下面四套是工厂冒烟示例（走完整生产清单，并已通过 `lint_theme.py`），用来对照四种结构模型，**不是**官方默认货架。用新气质时仍应重新走工厂，不要把它们当成主题超市来挑。

| id | 中文名 | 结构模型 |
|----|--------|----------|
| `mist-masthead` | 雾蓝刊头 | narrative / sparse / masthead / hairline / long-breath |
| `step-workshop` | 步骤工坊 | explainer / packed / numbered-chapter / soft-card / staccato |
| `paper-journal` | 纸页手记 | journal / balanced / labeled-rail / paper / documentary |
| `cinnabar-catalog` | 朱印目录 | catalog / packed / stamp / ink / staccato |

每次新风格都走工厂工作流，产出一个独立目录：

```
themes/{id}/
  theme.json      # 设计变量与结构模型（机器可读）
  THEME.md        # 槽位 HTML + 骨架 + 配方 + 映射（Agent 排版时只读这一份）
  preview.html    # 整页区块预览（给人看，不直接粘公众号）
```

渲染 Markdown 时按这个顺序找主题包：

1. 用户给出的路径
2. 当前工作目录 `./themes/{id}/`
3. skill 根目录 `themes/{id}/`
