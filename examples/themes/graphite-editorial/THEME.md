# 石墨刊读

## 结构模型

`narrative` / `sparse` / `masthead` / `hairline` / `long-breath`

叙事口吻。留白大于色块。标题靠超大编号和底边细线，几乎不用彩色。表面只有发丝线。段落用长呼吸行距。

## 设计变量

- 纸色 `#FAFAFA` · 墨色 `#18181B` · 说明 `#3F3F46`
- 主色 `#3F3F46` · 浅底 `#F4F4F5` · 浅底字 `#27272A`
- 点睛 `#71717A` · 线 `#E4E4E7` · 下划线 `#D4D4D8`
- 字体 sans · 正文字号 16px / 行高 1.9 · 标题上限 22px
- 圆角 0px · 阴影 none · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#FAFAFA;color:#18181B;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;padding:8px 4px 40px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 40px;padding:0 0 24px;border-bottom:1px solid #18181B;"><p style="margin:0 0 16px;font-size:11px;letter-spacing:0.32em;color:#3F3F46;line-height:1.6;"><span leaf="">{{kicker}}</span></p><p style="margin:0 0 16px;font-size:22px;font-weight:700;color:#18181B;line-height:1.4;letter-spacing:0.02em;"><span leaf="">{{title}}</span></p><p style="margin:0 0 16px;font-size:15px;color:#3F3F46;line-height:1.8;"><span leaf="">{{subtitle}}</span></p><p style="margin:0;font-size:12px;color:#71717A;letter-spacing:0.08em;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 36px;padding:0;"><p style="margin:0 0 12px;font-size:11px;letter-spacing:0.28em;color:#3F3F46;"><span leaf="">目录</span></p><p style="margin:0 0 8px;font-size:15px;color:#18181B;line-height:1.7;border-bottom:1px solid #E4E4E7;padding-bottom:8px;"><span leaf="">{{item1}}</span></p><p style="margin:0 0 8px;font-size:15px;color:#18181B;line-height:1.7;border-bottom:1px solid #E4E4E7;padding-bottom:8px;"><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#18181B;line-height:1.7;"><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:48px 0 18px;"><p style="margin:0 0 8px;font-size:24px;font-weight:700;color:#3F3F46;letter-spacing:0.08em;line-height:1;"><span leaf="">{{n}}</span></p><p style="margin:0 0 4px;font-size:11px;letter-spacing:0.24em;color:#71717A;"><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:18px;font-weight:700;color:#18181B;line-height:1.5;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:28px 0 12px;font-size:16px;font-weight:700;color:#18181B;line-height:1.5;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:28px 0 12px;font-size:15px;font-weight:700;color:#18181B;line-height:1.5;border-top:1px solid #18181B;padding-top:10px;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 20px;font-size:16px;color:#18181B;line-height:1.9;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="height:1px;background:#E4E4E7;margin:36px auto;max-width:48px;"><span leaf=""><br></span></section>
```

### slot:strong

```html
<span style="font-weight:700;color:#18181B;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#F4F4F5;color:#27272A;padding:0 3px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:2px solid #D4D4D8;font-weight:600;color:#18181B;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#3F3F46;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;color:#27272A;background:#F4F4F5;padding:1px 5px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:8px 0 24px;padding:12px 0;border-top:1px solid #E4E4E7;border-bottom:1px solid #E4E4E7;"><p style="margin:0;font-size:15px;color:#3F3F46;line-height:1.85;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 24px;padding:12px 0 12px 14px;border-left:1px solid #18181B;"><p style="margin:0 0 6px;font-size:12px;letter-spacing:0.18em;color:#18181B;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#18181B;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 24px;padding:12px 0 12px 14px;border-left:1px solid #18181B;"><p style="margin:0 0 6px;font-size:12px;letter-spacing:0.18em;color:#18181B;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#18181B;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:32px 0;padding:18px 0;border-top:1px solid #18181B;border-bottom:1px solid #18181B;"><p style="margin:0;font-size:18px;color:#18181B;line-height:1.7;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 22px;padding:0;"><p style="margin:0 0 8px;font-size:16px;color:#18181B;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p><p style="margin:0 0 8px;font-size:16px;color:#18181B;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#18181B;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 22px;padding:0;"><p style="margin:0 0 10px;font-size:16px;color:#18181B;line-height:1.8;"><span style="font-weight:700;color:#3F3F46;margin-right:10px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#18181B;line-height:1.8;"><span style="font-weight:700;color:#3F3F46;margin-right:10px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 24px;"><tr style="border-bottom:1px solid #18181B;"><th style="padding:8px 10px;font-size:13px;color:#18181B;text-align:left;border-bottom:1px solid #18181B;"><span leaf="">{{h1}}</span></th><th style="padding:8px 10px;font-size:13px;color:#18181B;text-align:left;border-bottom:1px solid #18181B;"><span leaf="">{{h2}}</span></th></tr><tr style="border-bottom:1px solid #E4E4E7;"><td style="padding:8px 10px;font-size:14px;color:#18181B;border-bottom:1px solid #E4E4E7;"><span leaf="">{{c1}}</span></td><td style="padding:8px 10px;font-size:14px;color:#18181B;border-bottom:1px solid #E4E4E7;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 24px;background:#18181B;padding:12px 0;"><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#FAFAFA;color:#D4D4D8;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#FAFAFA;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#FAFAFA;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 24px;background:#F4F4F5;padding:12px 0;border-top:1px solid #E4E4E7;border-bottom:1px solid #E4E4E7;"><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#18181B;color:#3F3F46;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#18181B;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#18181B;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 24px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#3F3F46;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 24px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#3F3F46;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 28px;padding:28px 16px;border:1.5px dashed #E4E4E7;text-align:center;background:#FAFAFA;"><p style="margin:0;font-size:14px;color:#3F3F46;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:48px 0 0;padding:20px 0 0;border-top:1px solid #18181B;"><p style="margin:0 0 8px;font-size:15px;color:#18181B;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#3F3F46;line-height:1.7;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:giant-num

```html
<p style="margin:36px 0 8px;font-size:24px;font-weight:700;color:#3F3F46;letter-spacing:0.12em;line-height:1;"><span leaf="">{{n}}</span></p>
```

### sig:hair-quote

```html
<section style="margin:32px 0;"><section style="height:1px;background:#18181B;margin:0 0 16px;"><span leaf=""><br></span></section><p style="margin:0;font-size:17px;color:#18181B;line-height:1.75;text-align:center;"><span leaf="">{{body}}</span></p><section style="height:1px;background:#18181B;margin:16px 0 0;"><span leaf=""><br></span></section></section>
```

### sig:geo-mark

```html
<section style="margin:40px 0 8px;text-align:center;"><section style="width:8px;height:8px;background:#18181B;margin:0 auto;"><span leaf=""><br></span></section><p style="margin:10px 0 0;font-size:11px;letter-spacing:0.28em;color:#3F3F46;"><span leaf="">{{mark}}</span></p></section>
```

### sig:thin-folio

```html
<p style="margin:0 0 24px;font-size:11px;letter-spacing:0.22em;color:#3F3F46;border-bottom:1px solid #E4E4E7;padding-bottom:10px;"><span leaf="">{{folio}}</span><span leaf="">  /  </span><span leaf="">{{volume}}</span></p>
```

### sig:slate-kicker

```html
<p style="margin:0 0 8px;font-size:11px;letter-spacing:0.36em;color:#71717A;"><span leaf="">{{label}}</span></p>
```

### sig:rule-spread

```html
<section style="margin:28px 0;padding:16px 0;border-top:1px solid #E4E4E7;border-bottom:1px solid #E4E4E7;"><p style="margin:0;font-size:15px;color:#18181B;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### sig:mute-note

```html
<section style="margin:0 0 24px;padding:0 0 0 12px;border-left:1px solid #E4E4E7;"><p style="margin:0;font-size:13px;color:#3F3F46;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### sig:quiet-byline

```html
<p style="margin:0 0 20px;font-size:13px;color:#3F3F46;border-top:1px solid #E4E4E7;padding-top:10px;"><span leaf="">{{body}}</span></p>
```

### sig:index-dot

```html
<p style="margin:0 0 8px;font-size:15px;color:#18181B;line-height:1.7;"><span style="color:#3F3F46;margin-right:8px;"><span leaf="">{{n}}</span></span><span leaf="">{{title}}</span></p>
```

### sig:chapter-rule

```html
<section style="margin:40px 0 12px;"><section style="height:1px;background:#18181B;max-width:32px;margin:0 0 8px;"><span leaf=""><br></span></section><p style="margin:0;font-size:11px;letter-spacing:0.24em;color:#3F3F46;"><span leaf="">{{label}}</span></p></section>
```

## 文章骨架

1. `root` 打开
2. `thin-folio`（可选）
3. `hero`
4. `toc`（在封面之后）
5. 章节循环：`giant-num` → `h2` → 段落 / `hair-quote`
6. `geo-mark`（可选）
7. `footer`
8. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + h2 + ol + callout_tip；可用签名槽 sig:index-dot；不要用 sig:hair-quote
- `listicle`: 核心槽 hero + toc + ul + h2；可用签名槽 sig:index-dot 与 sig:slate-kicker；不要用 sig:mute-note
- `opinion`: 核心槽 hero + quote_pull + paragraph + h2；可用签名槽 sig:hair-quote 与 sig:rule-spread；不要用 ol
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:quiet-byline；不要用 sig:giant-num
- `report`: 核心槽 hero + toc + table + h2；可用签名槽 sig:thin-folio；不要用 sig:geo-mark
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:hair-quote 与 sig:chapter-rule；不要用 table
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:mute-note；不要用 sig:slate-kicker

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
