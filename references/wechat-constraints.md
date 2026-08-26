# 微信公众号正文 HTML 约束

主题包里的每一个可粘贴组件、以及后续 Markdown 渲染产物，都必须按本节生成。预览壳（`assets/preview-shell.html`）可以含 `style`/`script`/`class`，因为它不会被复制进编辑器。

## 编辑器会做什么

粘贴进公众号图文编辑器后，平台会清洗 HTML：去掉外链样式和 `<style>` / `<script>`，剥离 `id`，丢掉不在白名单里的 CSS。能留下来的几乎只有**元素自身的 inline `style`**。因此主题不是 CSS 文件，而是「每个标签都带齐 style 的 HTML 零件」。

## 必须

- 容器用 `section` / `p` / `span`，媒体用 `img` / `figure` / `figcaption`，分隔用 `hr` 或空 `section`。
- 视觉全部写在当前元素的 `style` 上，色值写死为 `#RRGGBB` 或 `rgba(...)`。
- 可见中文文本包在 `<span leaf="">…</span>` 里。`span[leaf]` 是行内容器：里面只放文本、`img`、`br`、`strong`/`em`/`span`，**禁止再塞 `section`/`p`/`div`**。
- 装饰性空元素（色点、细线、色条）内部放 `<span leaf=""><br></span>`，否则空节点会被剥掉，样式一起消失。
- 字号拆开：同一个 `span[leaf]` 不要混两种 `font-size`；字号写在外层 `p`/`span` 上，leaf 只包文字。
- 正文标点用全角：`，。！？：；“”‘’（）——…`。代码块和行内代码保持原文。
- 正文字号 14–16px；任何标题/数字/封面字号 ≤ 24px（更大的字号容易被编辑器改写）。
- 图片：`max-width:100%;height:auto;display:block;margin:0 auto;`。不要用 `width:100%` 把小图拉糊。
- 代码块：每一行一个 `<p><span leaf="">…</span></p>`。缩进用全角空格 `　`。不要用 `white-space:pre`。
- 根容器宽度 `max-width:677px;margin:0 auto;`。

## 禁止（会丢样式或被改写）

| 写法 | 原因 |
|------|------|
| `<div>` | 编辑器常改写/拆掉，容器一律 `section` |
| `<style>` `<script>` `<link>` | 会被滤掉 |
| `class` / `id` | `id` 必剥；`class` 无样式表可挂，交付物禁止 |
| `position: fixed/absolute/sticky` | 不支持 |
| `float` | 不支持 |
| `@media` / `@keyframes` / `@import` | 不支持 |
| `display:grid` | 不支持；横向分组用上下堆叠 + 边框/留白 |
| `var(--x)` | 变量会被剥，必须写死 |
| 外链字体文件 | 不支持；只用系统字体栈 |
| `<svg>` `<canvas>` `<video>` `<audio>` `<iframe>` `<form>` `<button>` `<input>` | 不要出现在可粘贴正文 |
| 伪元素、hover、transition、backdrop-filter | 粘贴后不成立 |
| `gap` 作为主布局 | 部分客户端丢；子项用 `margin` |
| 用 `table` 做分栏/卡片宫格 | `table` 只用于真表格 |

`display:flex` 可以慎用（简单横排、垂直居中），但主题结构不能依赖复杂 flex 才能读得懂。即使 flex 退化成堆叠，阅读顺序仍要正确。

## 强调手段

- 正文强调：左竖条、药丸标签、下划线、浅底色块。
- 不要用四周 `border: … dashed` 去套标题。虚线框只留给「待补素材」居中占位。
- 主色是锚点，不是背景。大面积是纸色 + 灰阶，彩色只点睛。

## 字体栈

`theme.json` 的 `tokens.type.stack` 只允许下面五个值，渲染时展开为：

| stack | font-family |
|-------|-------------|
| `sans` | `-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif` |
| `serif` | `'Songti SC','STSong','SimSun',serif` |
| `kai` | `'Kaiti SC','STKaiti','KaiTi',serif` |
| `fangsong` | `'FangSong','STFangsong',serif` |
| `mono` | `'SF Mono',Consolas,Monaco,monospace` |

不要写外部 `@font-face`，不要写未在系统预装的品牌字体名。

## 占位与链接

- 预览里的配图用色块 `section` 模拟，不要编造图床 URL。
- 主题包占位文案必须是结构说明（「章节标题占位」），不要写成真实品牌/产品/城市。
- 正文里的「按钮」用带样式的 `span` 或 `a`，不要用 `<button>`。公众号外链能力有限，主题预览里避免假按钮点击态。
