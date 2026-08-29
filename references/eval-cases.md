# 回归用例

维护工厂或渲染合同时用。单次生产不必跑完全表。

## 工厂

| 用户说法 | 期望 |
|----------|------|
| 「按雾蓝杂志风做一套公众号主题」 | 只走工厂；写出三件套；不渲染文章（除非同时给了稿） |
| 只丢一张海报截图，「照这个气质做组件」 | 抽色与密度，不抄画面文字/Logo |
| 「先排这篇文章」但 `themes/` 为空 | 先收 brief 生产主题，再渲染；不即兴手写未入库主题 |
| 「用现成的摸鱼绿」 | 本 skill 无主题超市；说明需要生产或提供主题包路径 |
| 「做出石墨极简 / 禅意留白 / 教程绿卡那种气质」 | 按 design-system 气质表推导结构模型和色板，走工厂；不抄第三方组件库 HTML |
| `examples/themes/` 里有冒烟包 | 渲染发现仍只看 `themes/`；不要把示例当成货架 |
| 改「圆角改小、少阴影」 | 改 json + 预览 + THEME.md，重跑 lint |

## 渲染

| 用户说法 | 期望 |
|----------|------|
| 「用 `{id}` 把 a.md 转 HTML」 | 只读该包槽位；validate --strict；给预览页 |
| 同目录多套主题且未指定 | 询问，不擅自挑 |
| 文末已有作者三连 | 并入唯一 footer |
| 代码围栏 | 用 `code_dark` 或 `code_light`，不用 paragraph |
| `![](url)` 空 alt | 有图无说明组件 |

## 脚本

```bash
python3 scripts/selftest.py
python3 scripts/lint_theme.py themes
python3 scripts/lint_theme.py examples/themes
python3 scripts/validate_article.py --strict scripts/testdata/valid_article.html
```

`selftest.py` 必须覆盖：合法正文通过；含 `div`/`class`/无 leaf 的正文失败；事件属性与 `javascript:` URL 失败；`<pre><code>` 失败；代码文本里的禁用 CSS 不误报；`wrap_preview.py` 能生成外壳且复制区不含工具条 markup；主题包缺 HTML 围栏 / 签名槽 / 配方 / 预览覆盖则 lint 失败。
