# Hardware Metrics for Blog Deep Dives

Use this reference when a paper reports FPGA or ASIC implementation results.

The blog should preserve the paper's raw measurements and experimental conditions first. Derived metrics are secondary.

## Preserve raw results

Record when available:

- algorithm/version and parameter set;
- operation scope;
- FPGA device or ASIC process;
- tool/version and implementation stage;
- achieved frequency;
- LUT/FF/DSP/BRAM/URAM or ASIC area/gates/SRAM;
- cycle count;
- latency;
- initiation interval;
- throughput;
- power/energy;
- author-reported ATP/AT²P/throughput-area metric;
- exact author formula and units;
- whether I/O, host/software, external memory, or preprocessing are included.

Use `未报告` rather than guessing.

## Experimental setup table

Prefer one compact table in `5.1 Experimental Setup`.

Hardware numbers should never appear without enough context to tell what exact design point and operation they describe.

## Reported vs recomputed

Separate:

- **Reported** — copied from the paper.
- **Recomputed** — derived from reported raw values.
- **Normalized** — converted under a separately defined reference formula.
- **Analysis** — interpretation.

Never present a recomputed value as author-reported.

## Safe basic formulas

When cycles and frequency refer to the same design point:

`latency_s = cycles / frequency_Hz`

or:

`latency_us = cycles / frequency_MHz`

For steady-state throughput only when independent transactions can start every known initiation interval:

`throughput_ops_s = frequency_Hz / II_cycles`

Do not silently use `1/latency` as pipelined steady-state throughput.

Energy may be derived only when power and the execution window refer to the same workload/interval.

## ATP and area-time metrics

There is no universal FPGA area definition.

Always preserve the author's own formula first.

Examples include:

- `LUT × latency`;
- `A_equiv × latency`;
- `area × latency²`;
- paper-specific weighted LUT/DSP/BRAM formulas.

Do not compare values from different area definitions as if they were the same metric.

If the user has registered a trusted benchmark-paper formula, apply it only when:
- the required resources are reported;
- the operation boundary is compatible;
- the platform scope matches;
- the formula provenance is known.

Otherwise write `cannot compute`.

## FPGA resource discipline

Keep native resources visible separately:
- LUT;
- FF/register;
- DSP;
- BRAM;
- URAM;
- slices/ALMs if reported.

Do not invent universal weights.

## ASIC discipline

Record:
- process node;
- library/PVT/voltage when reported;
- synthesis/place-and-route/silicon stage;
- area/gates and SRAM inclusion;
- clock;
- power/energy method.

Do not normalize technology nodes by default.

## Single-paper default

For a normal blog deep dive:

1. reproduce the paper's most important hardware-results table;
2. attach experimental conditions;
3. preserve author metrics/formulas;
4. recompute only a few transparent quantities;
5. explain why the architecture changes the observed hardware cost.

Do not build a broad external ranking unless explicitly requested.

## Interpretation

ATP is an area-time cost, not direct utilization.

Do not infer PE occupancy, pipeline utilization, or memory efficiency from ATP alone. Use direct evidence such as bubbles, stalls, duty cycle, stage imbalance, and memory-port occupancy when available.
