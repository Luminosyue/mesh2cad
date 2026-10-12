# CADFS Complexity Bottleneck Report

## Finding

The current 125-case pilot is low-complexity and extrusion-biased. Full CADFS contains substantially more complex source histories, but the frozen lossless converter/schema is the main availability gate.

## Full Inventory Evidence

- Total CADFS source programs: 450,307.
- Core-supported / parse OK: 27,911.
- Extension-required: 416,494.
- Parse failures: 5,902.
- Extension-or-parse blocked: 422,396 (93.8%).
- Geometry-verified complex CADFS records found in frozen canonical evidence: 15.
- Explicit executable-but-not-geometry-verified complex records in frozen execution evidence: 0.

## Largest Capability Marginals

- REQUIRES_PROFILE_REFERENCE: 386,744
- REQUIRES_FACE_ATTACHED_SKETCH: 369,811
- REQUIRES_PROFILE_TOPOLOGY: 253,633
- REQUIRES_ARC_EXECUTION: 136,686
- REQUIRES_FILLET: 104,245
- REQUIRES_REVOLVE: 51,148
- REQUIRES_CHAMFER: 42,320
- REQUIRES_CONSTRUCTION_PLANE: 35,481
- REQUIRES_HOLE_SEMANTICS: 24,709
- REQUIRES_SHELL: 19,356
- REQUIRES_MIRROR: 12,070
- REQUIRES_SWEEP: 9,616
- REQUIRES_LOFT: 8,565
- REQUIRES_PATTERN: 7,191
- REQUIRES_ELLIPSE: 4,394

Marginal counts overlap and must not be summed. They identify the dominant missing capabilities: profile references, face-attached sketches, profile topology, arcs, and fillets.

## Audited Candidate Sample

The stratified CADFS audit1000 contains 892 complex records under the declared source-history rule; 149 are lossless candidates and 743 are unsupported complex candidates. `COMPLEX_CADFS_CANDIDATES_V1.json` stores all explicit Tier A/B records plus every qualifying Tier C record from audit1000.

## Recommendation

`BUILD_COMPLEX_CADFS_SUBSET`

This recommendation is not executed in this audit. The 15 existing complex, geometry-verified CADFS records beyond the current 125 are enough for a small next-stage subset. Broader expansion remains limited by converter coverage; no silent approximation is justified.
