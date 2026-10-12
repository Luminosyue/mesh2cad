# COMPACT_IR_TO_FUSION360_BACKEND_V1

## Scope and gates

This pilot deterministically compiles the frozen `14BIT_COMPACT_IR_V2` for PART_000, PART_001, and PART_005 into Fusion 360 Python feature code. It does not read canonical CadQuery source for generation, import STEP, re-quantize, resample, or change point counts.

```text
FUSION_CODE_GENERATION_GATE = 3/3 PASS
FUSION_STATIC_SYNTAX_GATE = 3/3 PASS
FUSION_RUNTIME_GATE = PENDING_FUSION360_HOST
TOKENIZER_ALIGNMENT_GATE = PASS
FUSION_DIRECT_TARGET_COMPRESSION_ADVANTAGE = NO
```

## Token statistics

| Part | Raw CadQuery | Compact IR | Fusion 360 API | Raw→Compact reduction | Raw→Fusion reduction | Compact→Fusion ratio |
|---|---:|---:|---:|---:|---:|---:|
| PART_000 | 5607 | 2810 | 4812 | 49.88% | 14.18% | 1.712 |
| PART_001 | 12917 | 6596 | 9800 | 48.94% | 24.13% | 1.486 |
| PART_005 | 25106 | 12850 | 18058 | 48.82% | 28.07% | 1.405 |

Counts use the same P1 tokenizer from the existing Airplane training run and include the EOS token. Sanity counts are exactly 2810, 6596, and 12850 for the three frozen `ir_v2` files.

### PART_000

`RAW_TOKEN_N=5607`  `COMPACT_TOKEN_N=2810`  `FUSION_TOKEN_N=4812`

### PART_001

`RAW_TOKEN_N=12917`  `COMPACT_TOKEN_N=6596`  `FUSION_TOKEN_N=9800`

### PART_005

`RAW_TOKEN_N=25106`  `COMPACT_TOKEN_N=12850`  `FUSION_TOKEN_N=18058`

## Backend coverage

| IR operation | Fusion implementation | Status |
|---|---|---|
| Workplane | ConstructionPlane offset + Sketch | PASS |
| spline | SketchFittedSpline with original q point order/count | PASS |
| loft | LoftFeature with exact section order | PASS |
| located | Matrix3D coordinate frame from origin/xDir/normal | PASS |
| translate | BRepBody.transformBy with scale and translation | PASS |
| xDir | Matrix3D x basis | PASS |
| normal | Matrix3D normal basis | PASS |

## Correctness and provenance

```text
SOURCE = 14BIT_COMPACT_IR_V2
FUSION_BACKEND_READS_CANONICAL_CADQUERY = NO
RE_QUANTIZATION = NO
SPLINE_RESAMPLE = NO
POINT_COUNT_CHANGED = NO
NORMALIZATION_CHANGED = NO
SECTION_ORDER_MATCH = TRUE
FUSION_FEATURE_LEVEL_CODE = YES
BACKEND_DECOUPLING_FEASIBLE = YES
FUSION_DIRECT_TARGET_COMPRESSION_ADVANTAGE = NO
```

## Interpretation

1. The three pilot parts are deterministically compilable to Fusion 360 Python source. The server cannot execute `adsk`, so runtime remains pending on a real Fusion 360 host.
2. Fusion source is longer than Compact IR for all three pilots because of Fusion imports, document/design setup, construction-plane and sketch creation, `ObjectCollection`/`Point3D` plumbing, fitted-spline and loft feature calls, and transform boilerplate.
3. Fusion source is shorter than the original Raw CadQuery source for all three pilots in this package, while retaining feature-level operations.
4. `spline`, `loft`, local frame, origin, xDir, and normal all have explicit semantic mappings. No spline point was changed.
5. The evidence favors `Mesh → Compact IR → deterministic backend → CadQuery/Fusion360`; the same frozen IR drives both backends.
6. All three pilot gates pass, so the package is ready for a controlled Airplane9 expansion after real-host runtime checks.

```text
IR_TO_FUSION_CODE_GENERATED = PASS
PYTHON_SYNTAX = PASS
SEMANTIC_MAPPING = PASS
COMPACT_IR_TO_FUSION_BACKEND_GATE = PASS
FUSION_RUNTIME_GATE = PENDING_HOST
READY_FOR_AIRPLANE9_FUSION_BACKEND = YES
```
