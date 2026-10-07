# Revise a PQC Hardware Paper Deep Dive Post

Use this workflow when the user points out problems in an existing `paper-deep-dive-*` post.

## 1. Classify feedback

Separate feedback into:

- factual/technical error;
- missing technical depth;
- structure/editorial problem;
- source-label overuse;
- missing figure/table;
- hardware-metric issue;
- unclear analysis/novelty claim;
- blog rendering/frontmatter issue.

Keep the existing cover during revisions. For a missing cover or an explicit request to replace it, follow `hero-image-usage.md`; use `--replace` for replacement. The selection script also updates the export manifest for HTML-imported posts.

## 2. Preserve verified content

Do not rewrite the whole article merely for style.

Keep:
- verified paper facts;
- correct formulas;
- useful figures;
- validated hardware tables;
- working links.

Rewrite only the affected sections plus any dependent statements.

## 3. Editorial repair rules

Common repairs:

- missing top card → add `PaperRating`;
- no arXiv → keep the card and omit arXiv-specific fields;
- missing overview discipline → add `一句话总结` and 2–5 `核心贡献` bullets;
- too many provenance markers → make paper prose natural and reduce to one `【Paper】` / `【Analysis】` block per subsection when possible;
- too much prose → convert contributions, settings, resources, limitations, or hypotheses into bullets/tables;
- weak experiments → enforce `5.1 Experimental Setup`, `5.2 Main Results`, `5.3 资源与效率分析`;
- weak method analysis → enforce `6.1 为什么有效？`, `6.2 核心创新`, `6.3 与已有方法的本质区别`, `6.4 代价与适用条件`.

## 4. Technical repair

Read `pqc-hardware-checklist.md` for domain gaps.

Read `hardware-metrics.md` when results/ATP/resource claims are involved.

Never introduce an implementation detail only to make the article look complete.

## 5. Dates

Update `updatedDate` for substantive revisions.

## 6. Validate

Run `pnpm check`.

Run `pnpm build` when shared components, schema, routes, or config were changed.
