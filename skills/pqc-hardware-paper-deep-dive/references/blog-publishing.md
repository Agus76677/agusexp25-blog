# 发布到 Hana / Astro 博客

完成 HTML/PDF 校验和逐页检查后，用 `scripts/publish_blog.py` 从同一份 `article.html` 导出博客文章。固定九章、原图、MathML、算法框和可见引用保持一致；标题进入博客原生目录。

```text
python "<skill-root>/scripts/publish_blog.py" --paper-dir "<paper-dir>" --blog-root "<blog-root>" --slug "<paper-slug>" --title "<中文标题>" --description "<160 字内摘要>" --tag hqc --build
```

导出位置：
- `src/content/blog/paper-deep-dive-<slug>/`：MDX、正文数据和样式组件。
- `public/papers/<slug>/`：正文引用的图像和解读 PDF。

目标博客包含 `scripts/select-paper-cover.mjs` 时，导出器会从个人图床目录自动选封面：优先未使用图片，同等条件随机选择，并写入 `heroImage` 及可用的 `pixivLink`。原生 MDX 与 HTML 导入共用此脚本，使用次数从已有文章读取。

- `--cover-category "芙莉莲"`：限定图片类别；省略时使用整个图片库。
- `--hero-image "https://pic.agusexp25.top/..."`：使用指定封面。
- 已有封面随修订保留；需要换图时加 `--replace-cover`。

仅补封面时，在博客根目录运行 `pnpm covers:select -- --post src/content/blog/paper-deep-dive-<slug>/index.mdx --write`，无需重新导出正文。脚本同步更新导入记录，使后续导出继续保留该封面。选图细则见目标博客的 `skills/paper-deep-dive/references/hero-image-usage.md`。

原论文 PDF、来源记录中的本地路径和工作文件留在论文目录。博客需要已有 Node.js 依赖；有 Astro `base` 配置时传入同值 `--base`。

首次接入时，将 `assets/components/paper-reading-time.mjs` 复制到博客 `src/plugins/`。在已有 `remarkReadingTime` 中导入 `paperReadingText`，保留 `file` 参数，并把正文取值改为 `paperReadingText(file) ?? mdastToString(tree)`。这让阅读时长统计包含导入正文；适配器使用 Hana 已有的 `node-html-parser`。图像继续使用博客的 `zoomable` 放大功能。

`--build` 执行本地检查和构建；加 `--publish` 则在构建通过后提交本次导出的文件并推送到 `origin/main`，由博客已有 GitHub Actions 部署。仓库和分支可用 `--remote`、`--branch` 指定。用户要求发布或试跑完整推送流程时可直接执行，否则先交付本地预览。

修订正文后重新生成 PDF，再用同一 slug 导出；首次发布日期保留，更新日期自动记录。正文修改在 `article.html` 完成。`--draft` 会设置博客草稿字段，静态资源仍属于公开站点资源。发布后检查 Actions 状态、文章网址、图像和 PDF 链接。

## 发布地址与入口核验

- 本博客的论文精读归入 `category: 'research'`，正式发布时不得设为草稿。统一阅读入口是 `https://agusexp25.top/blog/research/`，该列表根据文章分类自动生成卡片。
- 正文使用 `https://agusexp25.top/blog/paper-deep-dive-<slug>/`；Research 是分类列表，不是正文 URL 的父目录，无需另建 `/blog/research/<slug>/`。
- 发布完成后，除核对对应提交的部署结果，还必须打开 Research 列表，确认文章卡片及其排序位置，再从卡片进入正文，核验标题、内容与图片。新笔记按发布日期、修订按真实更新日期参与排序；卡片缺失或位置异常时检查分类、草稿状态、日期排序和分页，不能只凭正文 URL 返回成功就认定发布完成，也不要为置顶伪造更新日期。
