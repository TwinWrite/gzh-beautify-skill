# 步骤工坊

## 结构模型

`explainer` / `packed` / `numbered-chapter` / `soft-card` / `staccato`

说明文口吻。密度高，一块一事。标题是大号编号章节。表面是圆角柔阴影卡。节奏短促，步骤条和检查清单是签名。

## 设计变量

- 纸色 `#FFFFFF` · 墨色 `#1A2332` · 说明 `#4B5563`
- 主色 `#0F766E` · 浅底 `#E6F4F1` · 浅底字 `#115E59`
- 点睛 `#D97706` · 线 `#E2E8F0` · 下划线 `#5EEAD4`
- 字体 sans · 正文字号 15px / 行高 1.75 · 标题上限 20px
- 圆角 12px · 阴影 0 1px 4px · 根宽 677px

## 必选槽

### slot:root

```html
<section style="max-width:677px;margin:0 auto;background:#FFFFFF;color:#1A2332;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;padding:4px 2px 32px;"></section>
```

### slot:hero

```html
<section style="margin:0 0 20px;padding:18px 16px;background:#E6F4F1;border-radius:12px;box-shadow:0 1px 4px rgba(15,118,110,0.10);"><p style="margin:0 0 8px;font-size:12px;font-weight:700;color:#0F766E;letter-spacing:0.08em;"><span leaf="">{{kicker}}</span></p><p style="margin:0 0 8px;font-size:20px;font-weight:800;color:#115E59;line-height:1.4;"><span leaf="">{{title}}</span></p><p style="margin:0 0 10px;font-size:14px;color:#4B5563;line-height:1.7;"><span leaf="">{{subtitle}}</span></p><p style="margin:0;font-size:12px;color:#0F766E;font-weight:700;"><span leaf="">{{date}}</span></p></section>
```

### slot:toc

```html
<section style="margin:0 0 20px;padding:14px 16px;border:1px solid #E2E8F0;border-radius:12px;"><p style="margin:0 0 10px;font-size:13px;font-weight:800;color:#0F766E;"><span leaf="">本篇三步</span></p><p style="margin:0 0 6px;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">1. </span><span leaf="">{{item1}}</span></p><p style="margin:0 0 6px;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">2. </span><span leaf="">{{item2}}</span></p><p style="margin:0;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">3. </span><span leaf="">{{item3}}</span></p></section>
```

### slot:h2

```html
<section style="margin:28px 0 14px;padding:0;"><p style="margin:0 0 6px;font-size:24px;font-weight:800;color:#0F766E;line-height:1.2;"><span leaf="">{{n}}</span></p><p style="margin:0 0 4px;font-size:11px;letter-spacing:0.16em;color:#4B5563;"><span leaf="">{{en_label}}</span></p><p style="margin:0;font-size:18px;font-weight:800;color:#1A2332;line-height:1.4;"><span leaf="">{{title}}</span></p></section>
```

### slot:h3

```html
<p style="margin:18px 0 10px;font-size:16px;font-weight:800;color:#1A2332;line-height:1.45;"><span leaf="">{{title}}</span></p>
```

### slot:h3_label

```html
<p style="margin:18px 0 10px;font-size:14px;font-weight:800;color:#FFFFFF;background:#0F766E;display:inline-block;padding:4px 10px;border-radius:999px;line-height:1.4;"><span leaf="">{{title}}</span></p>
```

### slot:paragraph

```html
<p style="margin:0 0 14px;font-size:15px;color:#1A2332;line-height:1.75;"><span leaf="">{{body}}</span></p>
```

### slot:divider

```html
<section style="height:4px;width:28px;background:#0F766E;border-radius:4px;margin:20px 0;"><span leaf=""><br></span></section>
```

### slot:strong

```html
<span style="font-weight:800;color:#115E59;"><span leaf="">{{phrase}}</span></span>
```

### slot:mark

```html
<span style="background:#E6F4F1;color:#115E59;padding:0 4px;border-radius:4px;"><span leaf="">{{phrase}}</span></span>
```

### slot:underline

```html
<span style="border-bottom:2px solid #5EEAD4;font-weight:700;color:#1A2332;"><span leaf="">{{phrase}}</span></span>
```

### slot:strike

```html
<span style="text-decoration:line-through;color:#4B5563;"><span leaf="">{{phrase}}</span></span>
```

### slot:code_inline

```html
<span style="font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;background:#E6F4F1;color:#115E59;padding:1px 6px;border-radius:4px;"><span leaf="">{{phrase}}</span></span>
```

### slot:blockquote

```html
<section style="margin:0 0 16px;padding:12px 14px;background:#E6F4F1;border-radius:12px;border-left:4px solid #0F766E;"><p style="margin:0;font-size:14px;color:#1A2332;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_tip

```html
<section style="margin:0 0 16px;padding:12px 14px;background:#E6F4F1;border-radius:12px;"><p style="margin:0 0 4px;font-size:12px;font-weight:800;color:#0F766E;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:14px;color:#115E59;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:callout_warn

```html
<section style="margin:0 0 16px;padding:12px 14px;background:#FFFFFF;border-radius:12px;border-left:4px solid #D97706;"><p style="margin:0 0 4px;font-size:12px;font-weight:800;color:#1A2332;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:14px;color:#1A2332;line-height:1.7;"><span leaf="">{{body}}</span></p></section>
```

### slot:quote_pull

```html
<section style="margin:16px 0;padding:16px;background:#0F766E;border-radius:12px;"><p style="margin:0;font-size:16px;color:#FFFFFF;line-height:1.6;font-weight:700;"><span leaf="">{{body}}</span></p></section>
```

### slot:ul

```html
<section style="margin:0 0 16px;padding:12px 14px;background:#E6F4F1;border-radius:12px;"><p style="margin:0 0 8px;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">▸ </span><span leaf="">{{item}}</span></p><p style="margin:0 0 8px;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">▸ </span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">▸ </span><span leaf="">{{item}}</span></p></section>
```

### slot:ol

```html
<section style="margin:0 0 16px;padding:0;"><p style="margin:0 0 8px;font-size:15px;color:#1A2332;line-height:1.6;padding:10px 12px;background:#E6F4F1;border-radius:10px;"><span style="font-weight:800;color:#0F766E;margin-right:8px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p><p style="margin:0;font-size:15px;color:#1A2332;line-height:1.6;padding:10px 12px;background:#E6F4F1;border-radius:10px;"><span style="font-weight:800;color:#0F766E;margin-right:8px;"><span leaf="">{{n}}</span></span><span leaf="">{{item}}</span></p></section>
```

### slot:table

```html
<table style="width:100%;border-collapse:collapse;margin:0 0 16px;border-radius:12px;"><tr style="background:#0F766E;"><th style="padding:8px 10px;font-size:13px;font-weight:800;color:#FFFFFF;background:#0F766E;text-align:left;"><span leaf="">{{h1}}</span></th><th style="padding:8px 10px;font-size:13px;font-weight:800;color:#FFFFFF;background:#0F766E;text-align:left;"><span leaf="">{{h2}}</span></th></tr><tr style="background:#E6F4F1;"><td style="padding:8px 10px;font-size:14px;color:#1A2332;background:#E6F4F1;"><span leaf="">{{c1}}</span></td><td style="padding:8px 10px;font-size:14px;color:#1A2332;background:#E6F4F1;"><span leaf="">{{c2}}</span></td></tr></table>
```

### slot:code_dark

```html
<section style="margin:0 0 16px;background:#1A2332;border-radius:12px;padding:10px 0;box-shadow:0 1px 4px rgba(15,118,110,0.10);"><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FFFFFF;color:#5EEAD4;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FFFFFF;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#FFFFFF;"><span leaf="">{{line}}</span></p></section>
```

### slot:code_light

```html
<section style="margin:0 0 16px;background:#E6F4F1;border-radius:12px;padding:10px 0;"><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1A2332;color:#0F766E;"><span leaf="">{{lang}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1A2332;"><span leaf="">{{line}}</span></p><p style="margin:0;padding:2px 14px;font-family:'SF Mono',Consolas,Monaco,monospace;font-size:13px;line-height:1.65;color:#1A2332;"><span leaf="">{{line}}</span></p></section>
```

### slot:image

```html
<figure style="margin:0 0 16px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;border-radius:12px;"><figcaption style="margin:6px 0 0;font-size:12px;color:#4B5563;text-align:center;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:image_gif

```html
<figure style="margin:0 0 16px;"><img src="{{src}}" alt="{{alt}}" style="max-width:100%;height:auto;display:block;margin:0 auto;border-radius:12px;"><figcaption style="margin:6px 0 0;font-size:12px;color:#4B5563;text-align:center;"><span leaf="">{{caption}}</span></figcaption></figure>
```

### slot:media_ph

```html
<section style="margin:0 0 16px;padding:22px 12px;border:1.5px dashed #0F766E;border-radius:12px;text-align:center;background:#E6F4F1;"><p style="margin:0;font-size:14px;color:#115E59;"><span leaf="">{{body}}</span></p></section>
```

### slot:footer

```html
<section style="margin:28px 0 0;padding:14px 16px;background:#E6F4F1;border-radius:12px;"><p style="margin:0 0 6px;font-size:15px;font-weight:800;color:#115E59;"><span leaf="">{{author}}</span></p><p style="margin:0;font-size:13px;color:#4B5563;line-height:1.6;"><span leaf="">{{bio}}</span></p></section>
```

## 签名槽

### sig:step-rail

```html
<section style="margin:0 0 14px;padding:12px 14px;border-radius:12px;background:#FFFFFF;border:1px solid #E2E8F0;box-shadow:0 1px 4px rgba(15,118,110,0.10);"><p style="margin:0 0 6px;font-size:20px;font-weight:800;color:#0F766E;line-height:1.2;"><span leaf="">{{n}}</span></p><p style="margin:0;font-size:15px;color:#1A2332;line-height:1.6;"><span leaf="">{{body}}</span></p></section>
```

### sig:param-chip

```html
<p style="margin:0 0 10px;font-size:13px;color:#115E59;background:#E6F4F1;display:inline-block;padding:4px 10px;border-radius:999px;line-height:1.4;"><span leaf="">{{name}}</span><span leaf=""> = </span><span leaf="">{{value}}</span></p>
```

### sig:checklist-row

```html
<p style="margin:0 0 8px;font-size:15px;color:#1A2332;line-height:1.6;padding:8px 12px;background:#E6F4F1;border-radius:8px;"><span leaf="">☐ </span><span leaf="">{{item}}</span></p>
```

### sig:chapter-badge

```html
<p style="margin:0 0 8px;font-size:12px;font-weight:800;color:#FFFFFF;background:#0F766E;display:inline-block;padding:3px 10px;border-radius:999px;"><span leaf="">{{label}}</span></p>
```

### sig:tool-strip

```html
<section style="margin:0 0 14px;padding:10px 12px;background:#1A2332;border-radius:10px;"><p style="margin:0;font-size:13px;color:#FFFFFF;line-height:1.6;"><span leaf="">{{body}}</span></p></section>
```

### sig:outcome-card

```html
<section style="margin:0 0 14px;padding:14px;background:#E6F4F1;border-radius:12px;box-shadow:0 1px 4px rgba(15,118,110,0.10);"><p style="margin:0 0 6px;font-size:12px;font-weight:800;color:#0F766E;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:15px;color:#115E59;line-height:1.65;"><span leaf="">{{body}}</span></p></section>
```

### sig:do-dont

```html
<section style="margin:0 0 14px;padding:0;"><p style="margin:0 0 8px;font-size:14px;color:#115E59;padding:10px 12px;background:#E6F4F1;border-radius:10px;"><span leaf="">做：</span><span leaf="">{{do}}</span></p><p style="margin:0;font-size:14px;color:#1A2332;padding:10px 12px;background:#E6F4F1;border-radius:10px;"><span leaf="">不做：</span><span leaf="">{{dont}}</span></p></section>
```

### sig:recipe-head

```html
<p style="margin:0 0 12px;font-size:16px;font-weight:800;color:#1A2332;border-bottom:3px solid #D97706;padding-bottom:6px;display:inline-block;"><span leaf="">{{title}}</span></p>
```

### sig:progress-note

```html
<p style="margin:0 0 12px;font-size:13px;color:#4B5563;padding:8px 0;border-top:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;"><span leaf="">{{body}}</span></p>
```

### sig:pitfall-flag

```html
<section style="margin:0 0 14px;padding:12px 14px;border-left:4px solid #D97706;background:#FFFFFF;border-radius:0 12px 12px 0;"><p style="margin:0 0 4px;font-size:12px;font-weight:800;color:#1A2332;"><span leaf="">{{label}}</span></p><p style="margin:0;font-size:14px;color:#1A2332;line-height:1.65;"><span leaf="">{{body}}</span></p></section>
```

## 文章骨架

1. `root` 打开
2. `hero`
3. `toc`（紧跟封面，写成三步）
4. `recipe-head`（可选）
5. 章节循环：`chapter-badge` → `h2` → `step-rail` / 段落 / 清单
6. `outcome-card`
7. `footer`
8. `root` 关闭

## 文章类型配方

- `tutorial`: 核心槽 hero + ol + h2 + callout_tip；可用签名槽 sig:step-rail 与 sig:checklist-row；不要用 quote_pull
- `listicle`: 核心槽 hero + toc + ul + h2；可用签名槽 sig:param-chip 与 sig:chapter-badge；不要用 sig:pitfall-flag
- `opinion`: 核心槽 hero + paragraph + h2 + quote_pull；可用签名槽 sig:progress-note；不要用 sig:step-rail
- `interview`: 核心槽 hero + blockquote + paragraph；可用签名槽 sig:tool-strip；不要用 sig:checklist-row
- `report`: 核心槽 hero + table + h2 + toc；可用签名槽 sig:outcome-card；不要用 sig:do-dont
- `essay`: 核心槽 hero + paragraph + quote_pull；可用签名槽 sig:recipe-head；不要用 ol
- `case`: 核心槽 hero + h2 + ol + callout_warn；可用签名槽 sig:do-dont 与 sig:pitfall-flag；不要用 sig:chapter-badge

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
