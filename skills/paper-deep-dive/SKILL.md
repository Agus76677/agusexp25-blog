---
name: paper-deep-dive
description: Generate and revise Chinese blog-native deep dives for FPGA/ASIC post-quantum cryptography papers in the agusexp25-blog repository. Use for one-paper-per-post reading notes that emphasize algorithm-to-hardware mapping, architecture, memory/scheduling, implementation results, fair hardware metrics, and research insights.
---

# PQC Hardware Paper Deep Dive — Blog Edition

## Overview

Create one paper deep-dive post per paper under:

`src/content/blog/paper-deep-dive-<slug>/index.mdx`

This skill is the **blog renderer/editorial workflow** for PQC hardware paper reading. It should preserve the technical discipline of the standalone `pqc-hardware-paper-deep-dive` skill, but write directly in the blog's native MDX style.

## Workflow

Choose one workflow:

- **Generate post**: read `references/create-post.md`, `references/pqc-hardware-checklist.md`, and, when hardware results are reported, `references/hardware-metrics.md`; copy `assets/post-template.mdx`; then validate.
- **Revise post**: read `references/revise-post.md` and the relevant technical references; apply reader feedback without weakening factual accuracy; then validate.

When paper figures are needed, read `references/extract-paper-figures.md`.

When adding or replacing a cover, read `references/hero-image-usage.md` and use the blog's shared `scripts/select-paper-cover.mjs`.

## Shared Requirements

- Write in Chinese and keep important English technical terms.
- Do not create `index-en.mdx` unless explicitly requested.
- Use `category: 'research'` and the slug prefix `paper-deep-dive-`.
- Use the `PaperRating` card at the top of every generated post.
- The card must always contain a one-sentence takeaway and a recommendation rank, even when no arXiv ID exists.
- Do not fabricate arXiv IDs, DOI, venue, code, project URLs, or publication status.
- Prefer the paper's own figures for technical content. Upload blog-owned copies through the repository's image-upload workflow when appropriate.
- Do not use `pic.hana0721.top` or `Minakanmi-Yuki/picx-images-hosting` for new content.
- Default paper facts are written naturally. Do **not** prefix every paragraph with `【Paper】`.
- Use at most one compact `【Paper】` evidence block and one `【Analysis】` block per subsection unless a genuine source switch requires more.
- Use `【Code】` only for claims actually verified from released code/RTL.
- Use `【Source】` only for external primary sources such as standards/specifications or verified prior work.
- Prefer short natural paragraphs plus bullets/tables for contributions, design choices, experimental settings, and limitations.
- Keep each section's responsibility distinct and avoid repeating the same architecture description.
- Do not force NTT, complete-accelerator, ASIC, side-channel, or code-analysis content onto a paper that does not cover it.
- Validate with `pnpm check`. Run `pnpm build` when routes, config, schema, or shared components are changed.

## Editorial Target

The article should read like a polished research blog post rather than an evidence database.

Use this rhythm:

1. concise natural-language setup;
2. one structured list/table for the important facts;
3. one analysis paragraph when interpretation adds value.

The full evidence trail may live in the standalone deep-dive output; the blog should expose only the provenance labels needed for readers to distinguish paper claims, code facts, external sources, and independent analysis.

## Resources

- `references/create-post.md`: generation workflow, structure, card rules, source-label frequency, and writing style.
- `references/pqc-hardware-checklist.md`: PQC hardware technical dimensions.
- `references/hardware-metrics.md`: single-paper hardware-result recording and derived metrics.
- `references/extract-paper-figures.md`: extraction/upload rules for technical figures.
- `references/hero-image-usage.md`: cover-image policy for this blog.
- `references/revise-post.md`: reader-feedback revision workflow.
- `assets/post-template.mdx`: copyable MDX skeleton.
