# Create a PQC Hardware Paper Deep Dive Post

## Role

You are a PQC hardware paper analysis and technical-writing agent. Produce a deep reading note for researchers working on FPGA/ASIC acceleration of post-quantum cryptography.

The post should help the reader understand:

- what problem the paper solves;
- what the actual algorithmic/architectural mechanism is;
- how dataflow, memory, scheduling, and arithmetic interact;
- what was really measured on hardware;
- why the method works and what it costs;
- what remains useful for future research.

Do not write a generic summary or line-by-line translation.

## Source Priority

1. Original paper / supplementary material
2. Exact standard or specification when standard compliance matters
3. Official code or RTL
4. Official project page / artifact documentation
5. Closest primary prior work when needed
6. Other reliable sources

Never fill missing implementation details from intuition.

## Output Location

Create:

`src/content/blog/paper-deep-dive-<slug>/index.mdx`

Use `assets/post-template.mdx` as the starting point.

## Frontmatter

Use the blog's current schema.

Recommended form:

```yaml
---
title: '<paper-name> 论文精读'
publishDate: YYYY-MM-DD
updatedDate: YYYY-MM-DD
description: '<concise Chinese description under 160 chars>'
category: 'research'
tags:
  - 'paper deep dive'
  - 'pqc'
  - '<algorithm or topic>'
paper:
  arxivId: '<optional; omit when unavailable>'
  title: '<original paper title>'
  authors:
    - '<Author One>'
  venue: '<journal / conference / ePrint / arXiv>'
  year: YYYY
  code: '<official code URL or omit>'
  project: '<official project URL or omit>'
---
```

If the repository schema has already been extended with `paper.doi` and `paper.url`, populate them when verified. Otherwise do not invent substitute fields.

After writing the post, follow `references/hero-image-usage.md` to select a cover from the personal library and save `heroImage` (plus `pixivLink` when available). A user-provided cover takes priority.

## Paper Card

Every post must begin with `PaperRating`.

Required:
- `tldr`: exactly one useful sentence;
- `rank`: 1–5.

Optional:
- `arxivId`;
- `doi`;
- `paperUrl`;
- `publication`;
- code/project links.

No arXiv preprint is required. Missing identifiers must not suppress the card.

Example:

```mdx
<PaperRating
  doi='10.xxxx/xxxxx'
  paperUrl='https://publisher.example/paper'
  publication='TCHES 2026'
  tldr='一句话说明这篇论文真正解决了什么硬件问题，以及采用了什么机制。'
  rank={4}
/>
```

For an arXiv paper:

```mdx
<PaperRating
  arxivId='2602.08971'
  publication='arXiv'
  tldr='一句话总结。'
  rank={4}
/>
```

### Recommendation rank

Use the rank as an **editorial reading recommendation**, not as a scientific score:

- 5: highly relevant, strong evidence, and unusually reusable architectural insight;
- 4: strong and worth careful reading;
- 3: useful but narrower or less convincing;
- 2: limited relevance or evidence;
- 1: mostly skimmable for the current research direction.

## Required Structure

Use this structure as the default. Lower-level method subsections are adaptive.

```text
1. 论文概述
   一句话总结
   核心贡献

2. 背景与相关工作

3. 问题定义

4. 方法
   4.1 Overall Architecture
   4.2 核心机制 / Algorithm-to-Hardware Mapping
   4.3 算术与数据通路（相关时）
   4.4 存储与调度（相关时）
   4.5 代码/RTL 实现对照（有正式代码时）

5. 实验
   5.1 Experimental Setup
   5.2 Main Results
   5.3 资源与效率分析
   5.4 Ablation / Design-Space Exploration（有则写）

6. 方法分析
   6.1 为什么有效？
   6.2 核心创新
   6.3 与已有方法的本质区别
   6.4 代价与适用条件

7. 局限性
   7.1 作者明确提出的局限
   7.2 自己分析得到的局限

8. 启发与研究思考
```

Do not create empty subsections merely to satisfy the template.

## Section Rules

### 1. 论文概述

Start with a short orientation paragraph.

Then always include:

#### 一句话总结

One sentence only. Explain the mechanism and why it matters.

#### 核心贡献

Use 2–5 numbered bullets. Each bullet should be concrete and mechanism-oriented.

Good:
- “提出 conflict-free memory mapping，使 radix-4 butterfly 的并行访存无需额外 crossbar。”

Bad:
- “提高性能。”
- “优化硬件架构。”

### 2. 背景与相关工作

Keep this concise.

Preferred shape:
1. one short natural paragraph explaining the prerequisite;
2. one compact `【Paper】` block describing the gap identified by the authors;
3. one `【Analysis】` paragraph explaining how the paper sits in the design space.

Do not turn this section into a PQC textbook.

### 3. 问题定义

State only the problem needed to understand the paper:
- exact operation;
- algorithm/version/parameter set;
- mathematical domain and representation;
- implementation boundary;
- target optimization objective.

Use equations/tables only when they clarify hardware consequences.

### 4. 方法

#### 4.1 Overall Architecture

Show the most useful architecture/dataflow figure when available.

Give one concise end-to-end flow. Do not repeat the same flow in later subsections.

#### 4.2 Core mechanism / Algorithm-to-Hardware Mapping

Explain:
- original bottleneck;
- transformation or architectural choice;
- dependency change;
- datapath consequence;
- expected hardware benefit.

#### 4.3 Arithmetic and datapath

Use only when central to the paper.

Prefer bullets or a compact table for:
- arithmetic units;
- width/reduction;
- PE/BFU structure;
- pipeline stages;
- reuse/parallelism.

#### 4.4 Memory and scheduling

Use only when relevant.

Prefer:
- a schedule table;
- a bank/port table;
- a short bullet list of conflicts and solutions.

#### 4.5 Code/RTL correspondence

Only when official code/RTL is actually inspected.

Use `【Code】`. Map paper terminology to files/modules/FSM/memory structures. If no official implementation is available, omit the subsection or state this once.

### 5. 实验

#### 5.1 Experimental Setup

Use a compact table whenever possible.

Capture:
- FPGA device / ASIC process;
- tool/version;
- synthesis vs post-route vs silicon;
- parameter set;
- operation scope;
- frequency;
- parallelism/configuration;
- whether I/O, software, and external memory are included.

#### 5.2 Main Results

Reproduce the paper's key result table in a clean form when practical.

Explain the 2–4 most important results; do not narrate every table cell.

#### 5.3 Resource and Efficiency Analysis

Discuss LUT/FF/DSP/BRAM/URAM or ASIC area/power as applicable.

Preserve the author's ATP/AT²P definition. When a trusted canonical metric is available, label recomputation as `【Analysis】`.

Do not perform broad independent literature ranking by default.

#### 5.4 Ablation / Design-Space Exploration

Use only if the paper has meaningful architecture ablations, parameter sweeps, or multiple design points.

### 6. 方法分析

#### 6.1 为什么有效？

Explain the causal chain:

`bottleneck → mechanism → dependency/resource change → implementation effect → measured result`

#### 6.2 核心创新

Use 2–4 bullets.

Distinguish:
- mathematical transformation;
- datapath/microarchitecture;
- memory/scheduling;
- system integration;
- implementation engineering.

#### 6.3 与已有方法的本质区别

Prefer a small comparison table with rows such as:
- transform/decomposition;
- PE/BFU organization;
- memory mapping;
- scheduling;
- supported scope;
- cost introduced.

Do not claim “first” unless verified.

#### 6.4 代价与适用条件

State when the advantage may disappear:
- resource budget;
- parameter range;
- memory-port assumptions;
- routing/timing pressure;
- specialization;
- security requirements.

### 7. 局限性

Separate author-stated limitations from independent analysis.

Independent limitations work well as 3–6 numbered bullets.

### 8. 启发与研究思考

Do not list generic future work.

Prefer 1–3 testable research hypotheses:
- remaining bottleneck;
- mechanism to change;
- expected trade-off;
- minimum experiment;
- falsification condition.

## Source Labels

The body should read naturally.

### Default rule

Paper-derived prose is the default. Do **not** write `【Paper】` at the start of every paragraph.

### Recommended frequency

Within one subsection:
- use zero or one `【Paper】` block for an important cluster of sourced claims;
- use zero or one `【Analysis】` block for independent interpretation;
- use `【Code】` only when switching to verified code/RTL facts;
- use `【Source】` when relying on a standard/specification or external primary source.

A label can introduce a list/table and cover that cluster.

Example:

```mdx
这篇工作把主要瓶颈定位在访存冲突而不是蝶形运算本身。

**【Paper】**

1. 双端口 BRAM 无法直接支撑四路并行蝶形的任意地址组合。
2. 作者通过固定映射规则消除同周期 bank collision。
3. 调度因此不需要额外 stall。

**【Analysis】** 这意味着论文的主要贡献更接近 memory scheduling，而不是新的 NTT 数学算法。
```

Do not alternate labels sentence by sentence.

## Bullets, Tables, and Paragraphs

Prefer prose for:
- motivation;
- causal explanation;
- interpretation.

Prefer bullets for:
- contributions;
- module responsibilities;
- architectural choices;
- limitations;
- research hypotheses.

Prefer tables for:
- hardware setup;
- resource/performance results;
- design-point comparison;
- differences from prior architecture.

Avoid pages of unbroken prose.

## Figures

Read `references/extract-paper-figures.md`.

Use 3–6 figures only when they materially improve understanding:
- architecture/dataflow;
- PE/BFU/module diagram;
- memory mapping or scheduling;
- key implementation/result figure.

Tables already reproduced as Markdown usually do not need to be uploaded as screenshots.

## Technical Depth

Read `references/pqc-hardware-checklist.md`. Select only relevant categories.

When hardware results exist, also read `references/hardware-metrics.md`.

## Validation

Run:

```bash
pnpm check
```

Run:

```bash
pnpm build
```

when shared components, schema, routes, config, or rendering behavior change.
