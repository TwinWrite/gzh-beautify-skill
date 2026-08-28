# 苔色留白

## 结构模型

`journal` / `sparse` / `masthead` / `paper` / `long-breath`

手记口吻。留白远大于卡片。标题居中刊头。表面是纸色，几乎没有色块。节奏是长呼吸，一段一停。

## 设计变量

- 纸色 `#F7F6F2` · 墨色 `#2C2A26` · 说明 `#5C5B56`
- 主色 `#3E5348` · 浅底 `#E8EDE9` · 浅底字 `#2F4038`
- 点睛 `#8B7355` · 线 `#E4E1D8` · 下划线 `#C5D0C8`
- 字体 serif · 正文字号 16px / 行高 1.9 · 标题上限 22px
- 圆角 0px · 阴影 none · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#F7F6F2;color:#2C2A26;font-family:'Songti SC','STSong','SimSun',serif;padding:16px 8px 48px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 48px;padding:8px 0 0;text-align:center;"><p style="margin:0 0 20px;font-size:12px;letter-spacing:0.36em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{kicker}}</span></p><p style="margin:0 0 18px;font-size:22px;font-weight:700;color:#2C2A26;line-height:1.5;"><span leaf="">{{title}}</span></p><p style="margin:0 0 20px;font-size:15px;color:#5C5B56;line-height:1.9;"><span leaf="">{{subtitle}}</span></p><p style="margin:0;font-size:12px;color:#8B7355;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.12em;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 40px;padding:0;text-align:center;"><p style="margin:0 0 14px;font-size:12px;letter-spacing:0.28em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">目录</span></p><p style="margin:0 0 10px;font-size:15px;color:#2C2A26;line-height:1.8;"><span leaf="">{{item1}}</span></p><p style="margin:0 0 10px;font-size:15px;color:#2C2A26;line-height:1.8;"><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#2C2A26;line-height:1.8;"><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:52px 0 20px;text-align:center;"><p style="margin:0 0 8px;font-size:12px;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;"><span leaf="">{{n}}</span><span leaf=""> · </span><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:20px;font-weight:700;color:#2C2A26;line-height:1.5;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:32px 0 14px;font-size:17px;font-weight:700;color:#2C2A26;line-height:1.5;text-align:center;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:32px 0 14px;font-size:15px;font-weight:700;color:#3E5348;line-height:1.5;text-align:center;letter-spacing:0.08em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 22px;font-size:16px;color:#2C2A26;line-height:1.9;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="margin:40px 0;text-align:center;"><section style="height:1px;background:#E4E1D8;margin:0 auto;max-width:40px;"><span leaf=""><br></span></section></section>
```

### slot:strong

```html
<span style="font-weight:700;color:#2C2A26;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#E8EDE9;color:#2F4038;padding:0 3px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:1px solid #C5D0C8;font-weight:600;color:#2C2A26;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#5C5B56;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;color:#2F4038;background:#E8EDE9;padding:1px 5px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:16px 0 28px;padding:8px 0;"><p style="margin:0;font-size:16px;color:#5C5B56;line-height:1.95;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 28px;padding:0;"><p style="margin:0 0 8px;font-size:12px;letter-spacing:0.2em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 28px;padding:0;"><p style="margin:0 0 8px;font-size:12px;letter-spacing:0.2em;color:#2C2A26;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:36px 0;padding:8px 12px;"><p style="margin:0;font-size:18px;color:#2C2A26;line-height:1.8;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 24px;padding:0;"><p style="margin:0 0 10px;font-size:16px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0 0 10px;font-size:16px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">· </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">· </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 24px;padding:0;"><p style="margin:0 0 12px;font-size:16px;color:#2C2A26;line-height:1.9;text-align:center;"><span style="color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{n}}</span></span><span leaf="">  </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:16px;color:#2C2A26;line-height:1.9;text-align:center;"><span style="color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{n}}</span></span><span leaf="">  </span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 28px;"><tr style="border-bottom:1px solid #3E5348;"><th style="padding:10px 8px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#2F4038;text-align:left;border-bottom:1px solid #3E5348;"><span leaf="">{{h1}}</span></th><th style="padding:10px 8px;font-size:13px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#2F4038;text-align:left;border-bottom:1px solid #3E5348;"><span leaf="">{{h2}}</span></th></tr><tr style="border-bottom:1px solid #E4E1D8;"><td style="padding:10px 8px;font-size:14px;color:#2C2A26;border-bottom:1px solid #E4E1D8;"><span leaf="">{{c1}}</span></td><td style="padding:10px 8px;font-size:14px;color:#2C2A26;border-bottom:1px solid #E4E1D8;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 28px;background:#2C2A26;padding:14px 0;"><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F7F6F2;color:#C5D0C8;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F7F6F2;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#F7F6F2;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 28px;background:#E8EDE9;padding:14px 0;"><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#2C2A26;color:#3E5348;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#2C2A26;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:3px 18px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.7;color:#2C2A26;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 24px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#5C5B56;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 24px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;"><figcaption style="margin:8px 0 0;font-size:12px;color:#5C5B56;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 32px;padding:32px 16px;border:1.5px dashed #E4E1D8;text-align:center;background:#F7F6F2;"><p style="margin:0;font-size:14px;color:#5C5B56;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:56px 0 0;padding:24px 0 0;border-top:1px solid #E4E1D8;text-align:center;"><p style="margin:0 0 8px;font-size:15px;color:#2C2A26;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#5C5B56;line-height:1.8;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:breath-gap

```html
<section style="margin:28px 0;padding:12px 0;"><p style="margin:0;font-size:12px;letter-spacing:0.28em;color:#5C5B56;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{label}}</span></p></section>
```

### sig:centered-verse

```html
<section style="margin:36px 0;padding:8px 16px;"><p style="margin:0;font-size:17px;color:#2C2A26;line-height:1.9;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### sig:moss-rule

```html
<section style="margin:36px auto;text-align:center;"><section style="height:1px;background:#3E5348;margin:0 auto 8px;max-width:32px;"><span leaf=""><br></span></section><p style="margin:0;font-size:11px;letter-spacing:0.28em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p></section>
```

### sig:ink-dot

```html
<section style="margin:28px 0;text-align:center;"><section style="width:6px;height:6px;background:#3E5348;border-radius:6px;margin:0 auto;"><span leaf=""><br></span></section><p style="margin:8px 0 0;font-size:12px;color:#5C5B56;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;letter-spacing:0.2em;"><span leaf="">{{mark}}</span></p></section>
```

### sig:quiet-kicker

```html
<p style="margin:0 0 12px;font-size:12px;letter-spacing:0.32em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{label}}</span></p>
```

### sig:wide-quote

```html
<section style="margin:32px 0;padding:20px 8px;"><p style="margin:0;font-size:16px;color:#2F4038;line-height:1.95;text-align:center;"><span leaf="">{{body}}</span></p></section>
```

### sig:still-aside

```html
<p style="margin:0 0 24px;font-size:13px;color:#5C5B56;line-height:1.9;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{body}}</span></p>
```

### sig:date-seal

```html
<p style="margin:0 0 16px;font-size:12px;color:#8B7355;letter-spacing:0.16em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{date}}</span></p>
```

### sig:leaf-mark

```html
<section style="margin:32px 0 8px;text-align:center;"><p style="margin:0;font-size:12px;letter-spacing:0.4em;color:#3E5348;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"><span leaf="">{{label}}</span></p></section>
```

### sig:colophon-zen

```html
<p style="margin:28px 0;font-size:12px;color:#5C5B56;letter-spacing:0.14em;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;text-align:center;"><span leaf="">{{body}}</span></p>
```

## 文章骨架

1. `root` 打开
2. `quiet-kicker`（可选）
3. `hero`
4. `toc`（可选，封面之后）
5. 章节循环：`leaf-mark` → `h2` → 段落 / `centered-verse`
6. `ink-dot`（可选）
7. `footer`
8. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + h2 + ol + callout_tip；可用签名槽 sig:leaf-mark；不要用 sig:centered-verse
- `listicle`: 核心槽 hero + toc + ul + h2；可用签名槽 sig:still-aside；不要用 sig:wide-quote
- `opinion`: 核心槽 hero + paragraph + quote_pull + h2；可用签名槽 sig:centered-verse 与 sig:wide-quote；不要用 ol
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:date-seal；不要用 sig:quiet-kicker
- `report`: 核心槽 hero + table + toc + h2；可用签名槽 sig:colophon-zen；不要用 sig:breath-gap
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:centered-verse 与 sig:moss-rule；不要用 table
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:still-aside；不要用 sig:ink-dot

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
