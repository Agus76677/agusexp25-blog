# Hero Image Policy for Paper Deep Dive Posts

Use the personal cover library: [gallery](https://pic.agusexp25.top/covers/library/) · [catalog](https://pic.agusexp25.top/covers/library/catalog.json). It currently contains 362 user-selected images hosted on `pic.agusexp25.top`.

## Priority

Choose a hero image in this order:

1. a user-provided cover;
2. an image selected from the personal cover library;
3. a visually suitable figure from the paper, if using it as a cover is appropriate;
4. no hero image.

`heroImage` is optional in the blog schema. A missing cover must never block publication.

## Select a cover

After creating the MDX post, run from the blog root:

```bash
pnpm covers:select -- --post src/content/blog/paper-deep-dive-<slug>/index.mdx --write
```

The script writes `heroImage` with the hosted URL, dimensions and alt text, plus `pixivLink` when the catalog has a verified artwork ID. It reads existing article covers to prefer unused images, then the least-used images, choosing randomly among ties. Chinese/English versions in the same folder count as one article. The catalog's stored usage counters are not used.

- Use `--category "芙莉莲"`, `--category "动漫风景"` or `--category "边缘行者"` to filter by theme; omit it to use the whole library.
- Use `--id <image-id>` to choose a particular catalog entry.
- Existing covers are kept; add `--replace` only when the user asks for a different cover.
- Omit `--write` to preview the selection as JSON.

For a user-provided image, use the upload workflow below and put the returned URL in `heroImage.src`. Run selection once when preparing the article; builds simply render the saved cover. If the catalog is temporarily unavailable, retain an existing cover or add one when the catalog is available again.

## Upload

Use the repository's existing image workflow:

```bash
pnpm images:upload -- --dry-run <image>
pnpm images:upload -- <image>
```

Use the returned `https://pic.agusexp25.top/...` URL.

## Pixiv

The personal library includes the user-selected Hana covers hosted on this blog's own image domain. Keep each image's catalog source information; use its `pixivId` as `pixivLink` only when present.

## Technical figures

The hero cover is separate from the technical figures in the article body. Even with a decorative cover, the body should still include the paper's key architecture/method figures.
