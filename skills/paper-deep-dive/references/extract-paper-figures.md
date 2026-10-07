# Extract Paper Figures for agusexp25-blog

Use the paper's own technical figures. Prefer original source assets when available.

## 1. Source preference

Prefer, in order:

1. arXiv/ePrint LaTeX source or author artifact containing original figures;
2. official project/repository figure assets;
3. publisher/ePrint PDF;
4. user-provided PDF.

Do not require an arXiv ID. Many hardware papers are journal/conference publications without an arXiv preprint.

## 2. Choose figures

Normally use 3–6 figures only when they are genuinely useful.

For PQC hardware papers, prioritize:

- overall accelerator/dataflow architecture;
- BFU/PE/arithmetic-unit diagram;
- memory mapping/banking diagram;
- cycle/scheduling diagram;
- design-space/ablation figure;
- one result figure if a Markdown table cannot communicate it better.

Do not upload screenshots of tables that can be cleanly reproduced as Markdown.

## 3. Cropping

Preserve labels, legends, axis titles, and subfigure labels.

If LaTeX `trim`/`clip` values exist, preserve their semantics.

Use PDF rasterization/cropping tools supported by the local environment. Always visually inspect the final crop.

## 4. Upload to the user's image host

This repository already provides `scripts/upload-images.mjs`.

Dry-run first:

```bash
pnpm images:upload -- --dry-run --remote-dir blog/paper-deep-dive-<slug> <image-files>
```

Then upload:

```bash
pnpm images:upload -- --remote-dir blog/paper-deep-dive-<slug> <image-files>
```

The expected public prefix for this blog is:

`https://pic.agusexp25.top`

New posts must not use `pic.hana0721.top`.

## 5. Insert

Markdown:

```mdx
![<descriptive alt text>](https://pic.agusexp25.top/blog/paper-deep-dive-<slug>/<uploaded-file>.webp)
```

For wide figures:

```mdx
<img
  src='https://pic.agusexp25.top/blog/paper-deep-dive-<slug>/<uploaded-file>.webp'
  alt='<descriptive alt text>'
  class='zoomable'
  loading='lazy'
  decoding='async'
  style='max-width:100%; height:auto;'
/>
```

## 6. Verify

Verify the final public URL loads successfully before publishing.

If upload is unavailable, it is acceptable to keep a verified official figure URL temporarily, but document that choice. Do not invent a figure.

## 7. Provenance

In prose or caption, identify the original paper Figure/Table number when known.

Cropping and re-hosting do not change provenance.
