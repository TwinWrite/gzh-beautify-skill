# 主题包契约

一套主题是一个目录 `themes/{id}/`，三件套缺一不可。渲染文章时**只读这个目录**，不要再拼一份「通用组件库」。

```
themes/{id}/
  theme.json
  THEME.md
  preview.html
```

`id`：小写字母开头，只含 `a-z0-9-`，长度 3–40，**不要**加 `theme-` 前缀。目录名与 `theme.json` 的 `id` 必须相同。

## theme.json

字段以 [theme.schema.json](theme.schema.json) 为准。生产时先写这份，再生成 HTML，避免色值在预览和组件库里各写各的。

`slots` 数组必须列出下面 26 个必选槽，顺序不限。`signature_slots` 列出签名槽 id，必填、互不重复，8–16 个。

## THEME.md 章节（固定标题，lint 按标题抓）

```markdown
# {中文名}

## 结构模型
## 设计变量
## 必选槽
## 签名槽
## 文章骨架
## 文章类型配方
## Markdown 映射
```

### 必选槽

每个槽一个三级标题，格式严格为 `### slot:{id}`，后接一个 ` ```html ` 代码块。占位符用双花括号。

26 个必选槽：

| 槽 | Markdown / 用途 | 关键占位 |
|----|-----------------|----------|
| `root` | 全文最外层 | 无；其它槽放入其中 |
| `hero` | `# 标题` / 封面 | `{{kicker}}` `{{title}}` `{{subtitle}}` `{{date}}` |
| `toc` | 从 `##` 提炼 3 个看点 | `{{item1}}` `{{item2}}` `{{item3}}` |
| `h2` | `##` | `{{n}}` `{{en_label}}` `{{title}}` |
| `h3` | `###` | `{{title}}` |
| `h3_label` | 需要强调的小标题 | `{{title}}` |
| `paragraph` | 普通段落 | `{{body}}`（内部可再嵌 inline 槽） |
| `divider` | `---` | 无文案或装饰占位 |
| `strong` | `**x**` | `{{phrase}}` |
| `mark` | `==x==` | `{{phrase}}` |
| `underline` | 关键词下划线 / `++x++` | `{{phrase}}` |
| `strike` | `~~x~~` | `{{phrase}}` |
| `code_inline` | `` `x` `` | `{{phrase}}` |
| `blockquote` | 非开头的 `>` | `{{body}}` |
| `callout_tip` | 提示/旁注 | `{{label}}` `{{body}}` |
| `callout_warn` | 注意/警告 | `{{label}}` `{{body}}` |
| `quote_pull` | 金句 | `{{body}}` |
| `ul` | 无序列表（整组） | 重复 `{{item}}` 行 |
| `ol` | 有序列表（整组） | `{{n}}` `{{item}}` |
| `table` | 表格 | 表头/单元格占位 |
| `code_dark` | 围栏代码（默认） | `{{lang}}` 每行 `{{line}}` |
| `code_light` | 围栏代码（浅色主题气质） | 同上 |
| `image` | `![cap](src)` | `{{src}}`/`{{alt}}` 写在 `<img>` 属性上；`{{caption}}` 只出现在图注 |
| `image_gif` | `.gif` | 同上 |
| `media_ph` | `【插入…】` | `{{body}}` |
| `footer` | 文末签名 / CTA | `{{author}}` `{{bio}}` |

HTML 规则见 [wechat-constraints.md](wechat-constraints.md)。`THEME.md` 里的组件**禁止** `id`/`class`（预览页可以有）。

### 签名槽

标题格式 `### sig:{id}`。`id` 用英文短横线，要能看出结构模型（例如 `masthead-kicker`、`rail-digest`），不要叫 `card-1`。

### 文章骨架

用有序列表写出装配顺序，例如：

1. `root` 打开
2. `hero`
3. `toc`（若配方需要）
4. 章节循环：`h2` → 段落/块
5. `footer`
6. `root` 关闭

不同主题骨架可以不同，但必须写明 `toc` 相对 `hero` 的位置。骨架里出现、却被某条配方「不要用」的签名槽，必须标成「可选」，避免渲染时既强制插入又禁止。

### 文章类型配方

至少覆盖：`tutorial` `listicle` `opinion` `interview` `report` `essay` `case`。每行写：核心槽组合 + 可用签名槽 + 不要用的槽。

### Markdown 映射

一张表：Markdown 构造 → 槽 id。必选槽都要有行。行内标记按语义匹配，不要写死「组件 6e」这种与主题无关的编号。

## preview.html

给人在浏览器里**一次看完整套气质**。允许完整 HTML 文档、`id`、少量 `<style>`（只用于预览标注）。每个块上方可用浅灰小字标槽名。预览页**不是**公众号交付物，不要拿它去跑 `validate_article.py`。

预览必须覆盖全部必选槽 + 全部签名槽，占位文案用结构说明语。配图用色块，不编造图床。

## 槽位 HTML 解剖（示意，不是主题）

下面只示范 `h3_label` 该长什么样：inline style、leaf 包裹、主色当竖条。真正主题必须按自己的 tokens 重写，禁止复制这段当成品。

```html
<p style="margin:28px 0 14px;font-size:16px;font-weight:800;color:#1C1917;line-height:1.5;border-left:4px solid #334155;padding-left:12px;">
  <span leaf="">{{title}}</span>
</p>
```
