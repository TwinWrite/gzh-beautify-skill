# 朱印目录

## 结构模型

`catalog` / `packed` / `stamp` / `ink` / `staccato`

盘点口吻。条目密排。标题是朱印戳记：框线、居中、短标签。表面靠墨色块和印章边框，不靠阴影。节奏是一行一条的货架。

## 设计变量

- 纸色 `#FFFCF8` · 墨色 `#1F1611` · 说明 `#5C4E44`
- 主色 `#B42318` · 浅底 `#FBE8E6` · 浅底字 `#8A1A12`
- 点睛 `#1F4E79` · 线 `#E8DDD4` · 下划线 `#F0C4BE`
- 字体 fangsong · 正文字号 15px / 行高 1.75 · 标题上限 22px
- 圆角 0 · 阴影 none · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#FFFCF8;color:#1F1611;font-family:'FangSong','STFangsong',serif;padding:4px 2px 32px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 20px;padding:0;text-align:center;"><p style="margin:0 auto 10px;font-size:12px;color:#FFFCF8;background:#B42318;display:inline-block;padding:4px 12px;letter-spacing:0.2em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{kicker}}</span></p><p style="margin:12px 0 10px;font-size:22px;font-weight:700;color:#1F1611;line-height:1.4;"><span leaf="">{{title}}</span></p><p style="margin:0 0 10px;font-size:14px;color:#5C4E44;line-height:1.7;"><span leaf="">{{subtitle}}</span></p><p style="margin:0;font-size:12px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 20px;padding:12px;border:1px solid #B42318;"><p style="margin:0 0 8px;font-size:12px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;text-align:center;"><span leaf="">目次</span></p><p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;"><span leaf="">壹 · </span><span leaf="">{{item1}}</span></p><p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;"><span leaf="">贰 · </span><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#1F1611;line-height:1.6;"><span leaf="">叁 · </span><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:26px 0 12px;text-align:center;"><p style="margin:0 auto 8px;font-size:12px;color:#B42318;border:1px solid #B42318;display:inline-block;padding:2px 10px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.16em;"><span leaf="">{{n}}</span><span leaf=""> · </span><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:18px;font-weight:700;color:#1F1611;line-height:1.45;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:18px 0 10px;font-size:16px;font-weight:700;color:#1F1611;line-height:1.45;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:18px 0 10px;font-size:14px;font-weight:700;color:#B42318;border:1px solid #B42318;display:inline-block;padding:2px 8px;line-height:1.4;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 14px;font-size:15px;color:#1F1611;line-height:1.75;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="height:1px;background:#B42318;margin:18px auto;max-width:64px;"><span leaf=""><br></span></section>
```

### slot:strong

```html
<span style="font-weight:700;color:#B42318;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#FBE8E6;color:#8A1A12;padding:0 3px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:2px solid #F0C4BE;font-weight:700;color:#1F1611;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#5C4E44;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;color:#1F4E79;background:#FBE8E6;padding:0 4px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:0 0 16px;padding:10px 12px;border:1px solid #E8DDD4;"><p style="margin:0;font-size:14px;color:#5C4E44;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 16px;padding:10px 12px;background:#FBE8E6;border:1px solid #B42318;"><p style="margin:0 0 4px;font-size:12px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:14px;color:#8A1A12;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 16px;padding:10px 12px;border:1px solid #1F4E79;"><p style="margin:0 0 4px;font-size:12px;color:#1F4E79;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:14px;color:#1F1611;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:18px 0;padding:12px 8px;text-align:center;"><p style="margin:0 auto;font-size:16px;color:#B42318;line-height:1.6;border-top:1px solid #B42318;border-bottom:1px solid #B42318;padding:10px 8px;display:inline-block;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 16px;padding:0;"><p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;padding:8px 0;border-bottom:1px solid #E8DDD4;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;padding:8px 0;border-bottom:1px solid #E8DDD4;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:15px;color:#1F1611;line-height:1.6;padding:8px 0;border-bottom:1px solid #E8DDD4;"><span leaf="">· </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 16px;padding:0;"><p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;padding:8px 0;border-bottom:1px solid #E8DDD4;"><span style="color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;font-weight:700;"><span leaf="">{{n}}</span></span><span leaf="">  </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:15px;color:#1F1611;line-height:1.6;padding:8px 0;border-bottom:1px solid #E8DDD4;"><span style="color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;font-weight:700;"><span leaf="">{{n}}</span></span><span leaf="">  </span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 16px;border:1px solid #B42318;"><tr style="background:#B42318;"><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#FFFCF8;background:#B42318;text-align:left;"><span leaf="">{{h1}}</span></th><th style="padding:8px 10px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#FFFCF8;background:#B42318;text-align:left;"><span leaf="">{{h2}}</span></th></tr><tr style="border-bottom:1px solid #E8DDD4;"><td style="padding:8px 10px;font-size:14px;color:#1F1611;border-bottom:1px solid #E8DDD4;"><span leaf="">{{c1}}</span></td><td style="padding:8px 10px;font-size:14px;color:#1F1611;border-bottom:1px solid #E8DDD4;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 16px;background:#1F1611;padding:10px 0;"><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FBE8E6;color:#F0C4BE;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FBE8E6;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FBE8E6;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 16px;background:#FBE8E6;padding:10px 0;border:1px solid #E8DDD4;"><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1F1611;color:#B42318;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1F1611;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1F1611;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 16px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:6px 0 0;font-size:12px;color:#5C4E44;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span><span leaf="">{{alt}}</span><span leaf="">{{src}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 16px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:6px 0 0;font-size:12px;color:#5C4E44;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span><span leaf="">{{alt}}</span><span leaf="">{{src}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 16px;padding:22px 12px;border:1.5px dashed #B42318;text-align:center;background:#FFFCF8;"><p style="margin:0;font-size:14px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:28px 0 0;padding:16px 0 0;border-top:1px solid #B42318;text-align:center;"><p style="margin:0 0 6px;font-size:15px;color:#1F1611;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#5C4E44;line-height:1.6;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:stamp-mast

```html
<section style="margin:0 0 16px;text-align:center;"><p style="margin:0 auto;font-size:13px;color:#B42318;border:2px solid #B42318;display:inline-block;padding:8px 14px;letter-spacing:0.24em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;line-height:1.4;"><span leaf="">{{label}}</span></p></section>
```

### sig:item-ticket

```html
<section style="margin:0 0 12px;padding:10px 12px;border:1px solid #E8DDD4;border-left:4px solid #B42318;"><p style="margin:0 0 4px;font-size:12px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{n}}</span></p><p style="margin:0;font-size:15px;color:#1F1611;line-height:1.6;"><span leaf="">{{title}}</span></p></section>
```

### sig:rank-chip

```html
<p style="margin:0 0 10px;font-size:12px;font-weight:700;color:#FFFCF8;background:#B42318;display:inline-block;padding:2px 8px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{rank}}</span></p>
```

### sig:shelf-rule

```html
<section style="margin:14px 0;"><section style="height:1px;background:#E8DDD4;margin:0 0 6px;"><span leaf=""><br></span></section><p style="margin:0;font-size:11px;letter-spacing:0.18em;color:#5C4E44;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p></section>
```

### sig:pick-card

```html
<section style="margin:0 0 12px;padding:12px;background:#FBE8E6;border:1px solid #B42318;"><p style="margin:0 0 6px;font-size:12px;color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#8A1A12;line-height:1.65;"><span leaf="">{{body}}</span></p></section>
```

### sig:count-pill

```html
<p style="margin:0 0 10px;font-size:13px;color:#1F4E79;border:1px solid #1F4E79;display:inline-block;padding:2px 10px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{n}}</span><span leaf=""> 则</span></p>
```

### sig:series-mark

```html
<p style="margin:0 0 12px;font-size:12px;color:#5C4E44;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.16em;"><span leaf="">{{label}}</span></p>
```

### sig:footnote-ink

```html
<p style="margin:16px 0 8px;font-size:12px;color:#5C4E44;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;border-top:1px solid #E8DDD4;padding-top:8px;"><span leaf="">注：</span><span leaf="">{{body}}</span></p>
```

### sig:index-row

```html
<p style="margin:0 0 6px;font-size:15px;color:#1F1611;line-height:1.6;padding:6px 0;border-bottom:1px dotted #E8DDD4;"><span style="color:#B42318;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{n}}</span></span><span leaf="">  </span><span leaf="">{{title}}</span></p>
```

### sig:seal-end

```html
<section style="margin:24px 0 8px;text-align:center;"><p style="margin:0 auto;font-size:12px;color:#B42318;border:1px solid #B42318;display:inline-block;padding:6px;letter-spacing:0.2em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{mark}}</span></p></section>
```

## 文章骨架

1. `root` 打开
2. `stamp-mast`
3. `hero`
4. `toc`（封面后的目次框）
5. `count-pill`（可选）
6. 章节循环：`h2` → `item-ticket` / 段落
7. `seal-end`
8. `footer`
9. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + ol + h2 + callout_tip；可用签名槽 sig:index-row；不要用 sig:stamp-mast
- `listicle`: 核心槽 hero + toc + ul + h2；可用签名槽 sig:item-ticket 与 sig:rank-chip；不要用 quote_pull
- `opinion`: 核心槽 hero + paragraph + quote_pull + h2；可用签名槽 sig:series-mark；不要用 sig:item-ticket
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:footnote-ink；不要用 sig:rank-chip
- `report`: 核心槽 hero + table + toc + h2；可用签名槽 sig:count-pill 与 sig:shelf-rule；不要用 sig:pick-card
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:stamp-mast；不要用 ol
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:pick-card；不要用 sig:seal-end

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
