# 贡献指南

本仓库是**主题工厂**，不是主题货架。欢迎改进契约、校验脚本、工厂提示词与渲染合同。不要把「再内置一套默认主题」当作默认贡献方向。

## 结构

- `SKILL.md` — Agent 入口（分流：生产 / 渲染）
- `references/` — 平台约束、设计系统、主题契约、工厂、渲染合同
- `scripts/` — `lint_theme.py` / `validate_article.py` / `wrap_preview.py`
- `themes/` — 生产产出物（可空）
- `assets/` — 预览壳与试排稿

## 改完必跑

```bash
python3 scripts/selftest.py
python3 scripts/lint_theme.py themes
```

若你本地有主题包，再对一篇试排稿跑：

```bash
python3 scripts/validate_article.py --strict <正文.html>
```

`selftest.py` 必须全绿。`themes/` 为空时 lint 退出码为 0。

## 改契约时

必选槽、json 字段、THEME.md 章节标题是 Agent 与脚本的共同协议。改一处就要同步：

1. `references/theme.schema.json`
2. `references/theme-schema.md` / `theme-factory.md` / `SKILL.md`
3. `scripts/lint_theme.py` 里的常量
4. `scripts/selftest.py` 里的迷你主题夹具

## 提交

一个 PR 只做一件事。Commit 说明改了什么协议或哪条校验。不要提交本地 `*_排版_*.html`。
