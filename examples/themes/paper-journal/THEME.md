# 纸页手记

## 结构模型

`journal` / `balanced` / `labeled-rail` / `paper` / `documentary`

手记口吻。密度适中。标题靠左轨色条和栏目标签识别。表面是纸色，几乎无阴影。节奏像文献：日期戳、出处、页码。

## 设计变量

- 纸色 `#FBF7F0` · 墨色 `#3F2E22` · 说明 `#6B5748`
- 主色 `#8B5E3C` · 浅底 `#F3E6D4` · 浅底字 `#6B4226`
- 点睛 `#2F5D46` · 线 `#E4D5C1` · 下划线 `#D4B896`
- 字体 kai · 正文字号 16px / 行高 1.9 · 标题上限 20px
- 圆角 2px · 阴影 none · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#FBF7F0;color:#3F2E22;font-family:'Kaiti SC','STKaiti','KaiTi',serif;padding:6px 2px 36px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 28px;padding:4px 0 4px 16px;border-left:4px solid #8B5E3C;"><p style="margin:0 0 8px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.16em;"><span leaf="">{{kicker}}</span></p><p style="margin:0 0 10px;font-size:20px;font-weight:700;color:#3F2E22;line-height:1.5;"><span leaf="">{{title}}</span></p><p style="margin:0 0 10px;font-size:15px;color:#6B5748;line-height:1.8;"><span leaf="">{{subtitle}}</span></p><p style="margin:0;font-size:12px;color:#6B5748;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 28px;padding:12px 0 12px 16px;border-left:4px solid #E4D5C1;"><p style="margin:0 0 8px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.14em;"><span leaf="">摘录</span></p><p style="margin:0 0 6px;font-size:15px;color:#3F2E22;line-height:1.7;"><span leaf="">{{item1}}</span></p><p style="margin:0 0 6px;font-size:15px;color:#3F2E22;line-height:1.7;"><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#3F2E22;line-height:1.7;"><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:32px 0 16px;padding:0 0 0 14px;border-left:4px solid #8B5E3C;"><p style="margin:0 0 4px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{n}}</span><span leaf=""> / </span><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:18px;font-weight:700;color:#3F2E22;line-height:1.5;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:22px 0 10px;font-size:16px;font-weight:700;color:#3F2E22;line-height:1.5;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:22px 0 10px;font-size:14px;font-weight:700;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.08em;border-bottom:1px solid #8B5E3C;display:inline-block;padding-bottom:2px;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 16px;font-size:16px;color:#3F2E22;line-height:1.9;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="margin:28px 0;text-align:center;"><p style="margin:0 0 6px;font-size:12px;color:#E4D5C1;letter-spacing:0.4em;"><span leaf="">· · ·</span></p><section style="height:1px;background:#E4D5C1;margin:0 auto;max-width:72px;"><span leaf=""><br></span></section></section>
```

### slot:strong

```html
<span style="font-weight:700;color:#3F2E22;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#F3E6D4;color:#6B4226;padding:0 3px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:2px solid #D4B896;font-weight:600;color:#3F2E22;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#6B5748;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;color:#2F5D46;background:#F3E6D4;padding:0 4px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:0 0 20px;padding:8px 0 8px 14px;border-left:4px solid #E4D5C1;"><p style="margin:0;font-size:15px;color:#6B5748;line-height:1.85;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 20px;padding:12px 14px 12px 16px;background:#F3E6D4;border-left:4px solid #8B5E3C;"><p style="margin:0 0 6px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#6B4226;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 20px;padding:12px 14px 12px 16px;background:#F3E6D4;border-left:4px solid #2F5D46;"><p style="margin:0 0 6px;font-size:12px;color:#2F5D46;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#3F2E22;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:24px 0;padding:16px 8px 16px 16px;border-left:4px solid #3F2E22;"><p style="margin:0;font-size:17px;color:#3F2E22;line-height:1.75;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 18px;padding:0 0 0 16px;border-left:4px solid #E4D5C1;"><p style="margin:0 0 8px;font-size:16px;color:#3F2E22;line-height:1.8;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0 0 8px;font-size:16px;color:#3F2E22;line-height:1.8;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#3F2E22;line-height:1.8;"><span leaf="">· </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 18px;padding:0 0 0 16px;border-left:4px solid #8B5E3C;"><p style="margin:0 0 8px;font-size:16px;color:#3F2E22;line-height:1.8;"><span style="font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#8B5E3C;"><span leaf="">{{n}}</span></span><span leaf="">. </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#3F2E22;line-height:1.8;"><span style="font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#8B5E3C;"><span leaf="">{{n}}</span></span><span leaf="">. </span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 20px;"><tr style="border-bottom:1px solid #8B5E3C;"><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#6B4226;text-align:left;border-bottom:1px solid #8B5E3C;"><span leaf="">{{h1}}</span></th><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#6B4226;text-align:left;border-bottom:1px solid #8B5E3C;"><span leaf="">{{h2}}</span></th></tr><tr style="border-bottom:1px solid #E4D5C1;"><td style="padding:8px 10px;font-size:14px;color:#3F2E22;border-bottom:1px solid #E4D5C1;"><span leaf="">{{c1}}</span></td><td style="padding:8px 10px;font-size:14px;color:#3F2E22;border-bottom:1px solid #E4D5C1;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 20px;background:#3F2E22;padding:12px 0;"><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F3E6D4;color:#D4B896;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F3E6D4;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F3E6D4;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 20px;background:#F3E6D4;padding:12px 0;border-top:1px solid #E4D5C1;border-bottom:1px solid #E4D5C1;"><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#3F2E22;color:#8B5E3C;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#3F2E22;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#3F2E22;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 22px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#6B5748;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 22px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#6B5748;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 22px;padding:24px 12px;border:1.5px dashed #E4D5C1;text-align:center;background:#FBF7F0;"><p style="margin:0;font-size:14px;color:#6B5748;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:32px 0 0;padding:16px 0 0 16px;border-top:1px solid #E4D5C1;border-left:4px solid #8B5E3C;"><p style="margin:0 0 6px;font-size:15px;color:#3F2E22;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#6B5748;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:rail-digest

```html
<section style="margin:0 0 20px;padding:0 0 0 16px;border-left:4px solid #8B5E3C;"><p style="margin:0 0 6px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.14em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#3F2E22;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### sig:field-note

```html
<section style="margin:0 0 20px;padding:12px 14px;background:#F3E6D4;"><p style="margin:0 0 6px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#6B4226;line-height:1.85;"><span leaf="">{{body}}</span></p></section>
```

### sig:page-folio

```html
<p style="margin:0 0 16px;font-size:12px;color:#6B5748;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.18em;text-align:right;"><span leaf="">{{n}}</span></p>
```

### sig:excerpt-clip

```html
<section style="margin:0 0 20px;padding:14px 16px;border-top:1px solid #8B5E3C;border-bottom:1px solid #8B5E3C;"><p style="margin:0;font-size:15px;color:#3F2E22;line-height:1.85;"><span leaf="">{{body}}</span></p></section>
```

### sig:date-chip

```html
<p style="margin:0 0 12px;font-size:12px;color:#FBF7F0;background:#8B5E3C;display:inline-block;padding:2px 8px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.08em;"><span leaf="">{{date}}</span></p>
```

### sig:archive-head

```html
<p style="margin:0 0 14px;font-size:13px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;border-bottom:1px solid #E4D5C1;padding-bottom:8px;"><span leaf="">{{title}}</span></p>
```

### sig:afterword

```html
<section style="margin:24px 0 0;padding:12px 0 0 16px;border-left:4px solid #2F5D46;"><p style="margin:0 0 6px;font-size:12px;color:#2F5D46;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.14em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#3F2E22;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### sig:source-line

```html
<p style="margin:12px 0 20px;font-size:12px;color:#6B5748;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">出处：</span><span leaf="">{{body}}</span></p>
```

### sig:margin-label

```html
<p style="margin:0 0 8px;font-size:12px;color:#8B5E3C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;"><span leaf="">{{label}}</span></p>
```

### sig:blot-mark

```html
<section style="margin:20px 0;text-align:center;"><section style="width:10px;height:10px;background:#8B5E3C;border-radius:10px;margin:0 auto;"><span leaf=""><br></span></section><p style="margin:6px 0 0;font-size:12px;color:#6B5748;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{mark}}</span></p></section>
```

## 文章骨架

1. `root` 打开
2. `page-folio`（可选）
3. `hero`
4. `toc`（封面后的摘录轨）
5. `rail-digest`（可选）
6. 章节循环：`margin-label` → `h2` → 段落 / `field-note`
7. `afterword`（可选）
8. `footer`
9. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + h2 + ol + callout_tip；可用签名槽 sig:field-note；不要用 sig:afterword
- `listicle`: 核心槽 hero + ul + h2；可用签名槽 sig:margin-label 与 sig:rail-digest；不要用 sig:excerpt-clip
- `opinion`: 核心槽 hero + paragraph + quote_pull + h2；可用签名槽 sig:excerpt-clip；不要用 ol
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:source-line；不要用 sig:date-chip
- `report`: 核心槽 hero + table + toc + h2；可用签名槽 sig:archive-head 与 sig:page-folio；不要用 sig:blot-mark
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:afterword 与 sig:field-note；不要用 table
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:date-chip；不要用 sig:rail-digest

## Markdown 映射

| Markdown | 槽 |
|---|---|
| `#` 标题 | `hero` |
| 文首 `>` | `quote_pull 或 hero 副题` |
| `##` | `h2` |
| `###` | `h3 / h3_label` |
| 普通段落 | `paragraph` |
| `---` | `divider` |
| `**x**` | `strong` |
| `==x==` | `mark` |
| `++x++` | `underline` |
| `~~x~~` | `strike` |
| `` `x` `` | `code_inline` |
| 非开头 `>` | `blockquote` |
| 提示旁注 | `callout_tip` |
| 注意警告 | `callout_warn` |
| 金句 | `quote_pull` |
| 无序列表 | `ul` |
| 有序列表 | `ol` |
| 表格 | `table` |
| 围栏代码（深） | `code_dark` |
| 围栏代码（浅） | `code_light` |
| `![cap](src)` | `image` |
| `.gif` | `image_gif` |
| `【插入…】` | `media_ph` |
| 文末署名 | `footer` |
| 全文外壳 | `root` |
| 三看点 | `toc` |
