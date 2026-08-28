# 雾蓝刊头

## 结构模型

`narrative` / `sparse` / `masthead` / `hairline` / `long-breath`

叙事杂志口吻。留白大于卡片。标题走刊头：栏目字 + 衬线主标题 + 底边细线。表面只有发丝线，没有圆角阴影。段落用长呼吸行距。

## 设计变量

- 纸色 `#FAF8F4` · 墨色 `#1C1917` · 说明 `#5E574E`
- 主色 `#3D5A80` · 浅底 `#E4EBF3` · 浅底字 `#243F5C`
- 点睛 `#C45C26` · 线 `#D9D3C8` · 下划线 `#C5D4E0`
- 字体 serif · 正文字号 16px / 行高 1.9 · 标题上限 22px
- 圆角 0 · 阴影 none · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#FAF8F4;color:#1C1917;font-family:'Songti SC','STSong','SimSun',serif;padding:8px 4px 40px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 36px;padding:8px 0 0;border-bottom:1px solid #D9D3C8;"><p style="margin:0 0 14px;font-size:12px;letter-spacing:0.28em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;line-height:1.6;"><span leaf="">{{kicker}}</span></p><p style="margin:0 0 14px;font-size:22px;font-weight:700;color:#1C1917;line-height:1.45;letter-spacing:0.04em;"><span leaf="">{{title}}</span></p><p style="margin:0 0 18px;font-size:15px;color:#5E574E;line-height:1.8;"><span leaf="">{{subtitle}}</span></p><p style="margin:0 0 18px;font-size:12px;color:#5E574E;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.08em;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 36px;padding:0 0 0 16px;border-left:1px solid #3D5A80;"><p style="margin:0 0 10px;font-size:12px;letter-spacing:0.2em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">看点</span></p><p style="margin:0 0 8px;font-size:15px;color:#1C1917;line-height:1.7;"><span leaf="">{{item1}}</span></p><p style="margin:0 0 8px;font-size:15px;color:#1C1917;line-height:1.7;"><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#1C1917;line-height:1.7;"><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:44px 0 18px;padding:0 0 12px;border-bottom:1px solid #D9D3C8;"><p style="margin:0 0 6px;font-size:12px;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.16em;"><span leaf="">{{n}}</span><span leaf=""> · </span><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:20px;font-weight:700;color:#1C1917;line-height:1.5;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:28px 0 12px;font-size:17px;font-weight:700;color:#1C1917;line-height:1.5;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:28px 0 12px;font-size:16px;font-weight:700;color:#1C1917;line-height:1.5;border-left:3px solid #3D5A80;padding-left:12px;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 18px;font-size:16px;color:#1C1917;line-height:1.9;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="height:1px;background:#D9D3C8;margin:32px auto;max-width:88px;"><span leaf=""><br></span></section>
```

### slot:strong

```html
<span style="font-weight:700;color:#1C1917;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#E4EBF3;color:#243F5C;padding:0 4px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:2px solid #C5D4E0;font-weight:600;color:#1C1917;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#5E574E;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;color:#243F5C;background:#E4EBF3;padding:1px 5px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:8px 0 24px;padding:4px 0 4px 16px;border-left:1px solid #D9D3C8;"><p style="margin:0;font-size:15px;color:#5E574E;line-height:1.85;font-style:italic;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 24px;padding:14px 0 14px 16px;border-left:2px solid #3D5A80;"><p style="margin:0 0 6px;font-size:12px;letter-spacing:0.18em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#1C1917;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 24px;padding:14px 0 14px 16px;border-left:2px solid #C45C26;"><p style="margin:0 0 6px;font-size:12px;letter-spacing:0.18em;color:#C45C26;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#1C1917;line-height:1.8;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:28px 0;padding:20px 8px;border-top:1px solid #1C1917;border-bottom:1px solid #1C1917;"><p style="margin:0;font-size:18px;color:#1C1917;line-height:1.7;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 22px;padding:0;"><p style="margin:0 0 8px;font-size:16px;color:#1C1917;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p><p style="margin:0 0 8px;font-size:16px;color:#1C1917;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#1C1917;line-height:1.8;"><span leaf="">— </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 22px;padding:0;"><p style="margin:0 0 10px;font-size:16px;color:#1C1917;line-height:1.8;"><span style="color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;margin-right:8px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#1C1917;line-height:1.8;"><span style="color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;margin-right:8px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 24px;"><tr style="border-bottom:1px solid #D9D3C8;"><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#243F5C;background:#E4EBF3;text-align:left;border-bottom:1px solid #D9D3C8;"><span leaf="">{{h1}}</span></th><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#243F5C;background:#E4EBF3;text-align:left;border-bottom:1px solid #D9D3C8;"><span leaf="">{{h2}}</span></th></tr><tr style="border-bottom:1px solid #D9D3C8;"><td style="padding:8px 10px;font-size:14px;color:#1C1917;border-bottom:1px solid #D9D3C8;"><span leaf="">{{c1}}</span></td><td style="padding:8px 10px;font-size:14px;color:#1C1917;border-bottom:1px solid #D9D3C8;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 24px;background:#1C1917;padding:12px 0;"><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#E7E2D8;color:#A8C0D4;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#E7E2D8;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#E7E2D8;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 24px;background:#E4EBF3;padding:12px 0;border:1px solid #D9D3C8;"><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#1C1917;color:#3D5A80;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#1C1917;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 16px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#1C1917;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 28px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#5E574E;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span><span leaf="">{{alt}}</span><span leaf="">{{src}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 28px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#5E574E;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span><span leaf="">{{alt}}</span><span leaf="">{{src}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 28px;padding:28px 16px;border:1.5px dashed #D9D3C8;text-align:center;background:#FAF8F4;"><p style="margin:0;font-size:14px;color:#5E574E;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:40px 0 0;padding:20px 0 0;border-top:1px solid #1C1917;"><p style="margin:0 0 8px;font-size:15px;color:#1C1917;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#5E574E;line-height:1.7;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:masthead-folio

```html
<section style="margin:0 0 28px;padding:0 0 12px;border-bottom:1px solid #1C1917;"><p style="margin:0;font-size:12px;letter-spacing:0.22em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{folio}}</span><span leaf="">  /  </span><span leaf="">{{volume}}</span></p></section>
```

### sig:editor-note

```html
<section style="margin:0 0 28px;padding:16px 18px;background:#E4EBF3;"><p style="margin:0 0 8px;font-size:12px;letter-spacing:0.2em;color:#243F5C;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#243F5C;line-height:1.85;"><span leaf="">{{body}}</span></p></section>
```

### sig:pull-spread

```html
<section style="margin:32px 0;"><section style="height:1px;background:#1C1917;margin:0 auto 16px;max-width:48px;"><span leaf=""><br></span></section><p style="margin:0 12px;font-size:18px;color:#1C1917;line-height:1.75;text-align:center;"><span leaf="">{{body}}</span></p><section style="height:1px;background:#1C1917;margin:16px auto 0;max-width:48px;"><span leaf=""><br></span></section></section>
```

### sig:chapter-ornament

```html
<section style="margin:36px 0 8px;text-align:center;"><p style="margin:0;font-size:12px;letter-spacing:0.4em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p></section>
```

### sig:colophon-line

```html
<p style="margin:24px 0;font-size:12px;color:#5E574E;letter-spacing:0.12em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{body}}</span></p>
```

### sig:issue-kicker

```html
<p style="margin:0 0 8px;font-size:11px;letter-spacing:0.32em;color:#C45C26;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p>
```

### sig:margin-aside

```html
<section style="margin:0 0 24px;padding:0 0 0 14px;border-left:1px dotted #D9D3C8;"><p style="margin:0;font-size:13px;color:#5E574E;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p></section>
```

### sig:end-mark

```html
<section style="margin:36px 0 8px;text-align:center;"><section style="width:8px;height:8px;background:#3D5A80;margin:0 auto;"><span leaf=""><br></span></section><p style="margin:8px 0 0;font-size:12px;color:#5E574E;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;"><span leaf="">{{mark}}</span></p></section>
```

### sig:verse-rule

```html
<section style="margin:28px auto;text-align:center;"><section style="height:1px;background:#3D5A80;margin:0 auto 8px;max-width:40px;"><span leaf=""><br></span></section><p style="margin:0;font-size:11px;letter-spacing:0.28em;color:#3D5A80;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p></section>
```

### sig:byline-hair

```html
<p style="margin:0 0 20px;font-size:13px;color:#5E574E;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;border-top:1px solid #D9D3C8;padding-top:10px;"><span leaf="">{{body}}</span></p>
```

## 文章骨架

1. `root` 打开
2. `masthead-folio`（可选）
3. `hero`
4. `toc`（在封面之后）
5. `editor-note`（评论/随笔可用）
6. 章节循环：`chapter-ornament` → `h2` → 段落/块
7. `end-mark`
8. `footer`
9. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + h2 + ol + callout_tip；可用签名槽 sig:chapter-ornament；不要用 sig:pull-spread
- `listicle`: 核心槽 hero + toc + ul + h2；可用签名槽 sig:margin-aside；不要用 sig:editor-note
- `opinion`: 核心槽 hero + quote_pull + paragraph + h2；可用签名槽 sig:editor-note 与 sig:pull-spread；不要用 ol
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:byline-hair；不要用 sig:issue-kicker
- `report`: 核心槽 hero + toc + table + h2；可用签名槽 sig:colophon-line；不要用 sig:verse-rule
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:pull-spread 与 sig:end-mark；不要用 table
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:masthead-folio；不要用 sig:editor-note

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
