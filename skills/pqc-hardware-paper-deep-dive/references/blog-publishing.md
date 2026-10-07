# 发布到 Hana / Astro 博客

完成 HTML/PDF 校验和逐页检查后，用 `scripts/publish_blog.py` 从同一份 `article.html` 导出博客文章。固定九章、原图、MathML、算法框和可见引用保持一致；标题进入博客原生目录。

```text
python "<skill-root>/scripts/publish_blog.py" --paper-dir "<paper-dir>" --blog-root "<blog-root>" --slug "<paper-slug>" --title "<中文标题>" --description "<160 字内摘要>" --tag hqc --build
```

导出位置：
- `src/content/blog/paper-deep-dive-<slug>/`：MDX、正文数据和样式组件。
- `public/papers/<slug>/`：正文引用的图像和解读 PDF。

原论文 PDF、来源记录中的本地路径和工作文件留在论文目录。博客需要已有 Node.js 依赖；有 Astro `base` 配置时传入同值 `--base`。

首次接入时，将 `assets/components/paper-reading-time.mjs` 复制到博客 `src/plugins/`。在已有 `remarkReadingTime` 中导入 `paperReadingText`，保留 `file` 参数，并把正文取值改为 `paperReadingText(file) ?? mdastToString(tree)`。这让阅读时长统计包含导入正文；适配器使用 Hana 已有的 `node-html-parser`。图像继续使用博客的 `zoomable` 放大功能。

`--build` 执行本地检查和构建；加 `--publish` 则在构建通过后提交本次导出的文件并推送到 `origin/main`，由博客已有 GitHub Actions 部署。仓库和分支可用 `--remote`、`--branch` 指定。用户要求发布或试跑完整推送流程时可直接执行，否则先交付本地预览。

修订正文后重新生成 PDF，再用同一 slug 导出；首次发布日期保留，更新日期自动记录。正文修改在 `article.html` 完成。`--draft` 会设置博客草稿字段，静态资源仍属于公开站点资源。发布后检查 Actions 状态、文章网址、图像和 PDF 链接。
