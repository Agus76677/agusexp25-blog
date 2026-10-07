# PQC Hardware Domain Checklist

Select only categories that the paper actually covers. Use this as an attention map, not a questionnaire.

## Algorithm and implementation scope

- Algorithm family, exact scheme/version, parameter set, security level, and specification status.
- Implemented scope: arithmetic kernel, transform, polynomial multiplication, KeyGen, Encaps/Decaps, Sign/Verify, or complete accelerator.
- Mathematical domain, coefficient representation, dimensions, and correctness conditions.
- Hardware/software/precomputation boundary.

## Arithmetic and algorithmic kernels

- Dominant kernels and their share of computation.
- Polynomial/vector/matrix operations, finite-field arithmetic, modular multiplication/reduction, transforms, sampling, hashing, encoding/decoding.
- Mathematical transformations that reduce operation count, expose parallelism, simplify arithmetic, or improve locality.
- Operand width, intermediate range, reduction strategy, precision, and representation.
- Arithmetic complexity versus control, memory traffic, and hardware cost.

## Lattice-based cryptography

- Ring structure, matrix-vector multiplication, coefficient/transform-domain representation.
- NTT/INTT: radix, CT/GS, butterfly form, stage scheduling, scaling, permutation, twiddle handling.
- Complete/incomplete transforms and point-wise multiplication.
- Montgomery/Barrett/specialized/lazy reduction.
- Sampling, compression, rounding/decomposition/hints, rejection, and Keccak/SHAKE integration when relevant.
- Reuse across ML-KEM/Kyber, ML-DSA/Dilithium, Falcon, or related schemes.

## Code-based cryptography

- Code structure, algebraic representation, encoding/decoding method, dominant bottlenecks.
- Binary polynomial arithmetic, sparse/dense representation, cyclic convolution, fixed-weight sampling, finite-field operations when applicable.
- Decoder architecture, iterations, parallelism, memory organization, lookup/computation trade-offs, failure behavior.
- Relationship between parameters, decoding complexity, memory footprint, and parallelism.
- Whole-KEM balance among polynomial operations, coding/decoding, sampling, hashing, and re-encryption checks.

## Polynomial multiplication and transforms

- Schoolbook, Karatsuba, Toom-Cook, NTT, FFT, hybrid or other decomposition.
- Decomposition depth, transform size, reconstruction.
- Multipliers, adders, reducers, BFUs/PEs, reuse.
- Pipeline organization, stage fusion/sharing.
- Data ordering, permutation/reordering, memory banking.
- Whether arithmetic savings actually reduce latency, area, or area-time cost.

## Datapath and microarchitecture

- PE organization, pipeline depth, real parallelism, resource sharing.
- Interfaces between arithmetic, memories, controller, and top-level phases.
- Critical path candidates, fanout, mux depth, routing pressure.
- Cycle-level dependencies, fill/drain, initiation interval.
- Specialization versus configurability.

## Memory architecture and scheduling

- BRAM/URAM/SRAM/register/ROM organization, banking, ports, footprint.
- Address generation, buffering, ping-pong, conflicts, intermediate storage.
- Reuse, locality, bandwidth, arithmetic-memory balance.
- Twiddle/constants/precomputation storage.
- Reordering and format-conversion cost.
- Memory-limited versus compute-limited behavior.

## Complete and unified accelerators

- End-to-end KeyGen/Encaps/Decaps/Sign/Verify flow.
- Module-level latency/bottleneck distribution.
- Rate matching among arithmetic, hashing, sampling, coding, and memory.
- Cross-phase module reuse and utilization.
- Multi-algorithm sharing, configuration overhead, and cost of generality.

## FPGA / ASIC implementation

- Device or process, tools, implementation stage.
- FPGA: LUT/FF/DSP/BRAM/URAM/slices/ALMs.
- ASIC: area/gates, SRAM inclusion, frequency, power/energy.
- Target versus achieved frequency and timing closure.
- I/O/host/external-memory inclusion.

## Performance and efficiency

- Cycles, latency, II, throughput, frequency.
- Resource breakdown.
- Author-defined ATP/AT²P or other efficiency metric.
- Relationship between parallelism and resource growth.
- Whether improvement comes from operation count, unit cost, memory traffic, scheduling/utilization, or frequency.

## Correctness, standards, and security

- Reference/KAT/software validation.
- Range, precision, reduction, truncation, overflow.
- Exact specification/standard revision and deviations.
- Secret-dependent control/access, constant-time behavior.
- Side-channel/fault countermeasures only when relevant to the paper.

## Code / RTL correspondence

- Paper modules/equations to RTL/source files, parameters, FSM, address generation, memories, testbench.
- Tool scripts, constraints, commit/version.
- Differences between paper and released artifact.
- Missing pieces needed for reproduction.

## Novelty and research opportunities

- Closest prior mechanism and the exact difference.
- Bottleneck removed or shifted.
- Cost introduced by the proposed mechanism.
- Remaining bottleneck.
- Transferable mechanism across algorithms/parameters/platforms.
- Testable hypothesis, minimum experiment, and falsification condition.
