# PROGRAM_PARAMETER_ERROR_DIAGNOSTIC_V1

CURRENT_GATE = PROGRAM_PARAMETER_ERROR_DIAGNOSTIC_V1_COMPLETE

## Answer-first conclusion

PRIMARY_BOTTLENECK = GLOBAL_PLACEMENT
SECONDARY_BOTTLENECK = FEATURE_PARAMETER
CURRENT_REPRESENTATION_MAINLY_ENCODES_WHAT_OVER_WHERE = YES

M2 fixes operation/profile primitive identity in the three official OpF1 rescue cases, but OpF1 ignores order and all numeric values. The matched-operation audit therefore explains the geometry plateau through the remaining placement, curve/profile, and feature-parameter errors rather than parse or STEP validity.

## Fixed data

- Held-out: 25/25 aligned; GT/B0/M2 parse: 25/25.
- No training, decoding, model changes, Dora, Dev50, or Test100 access.
- M2 rescue IDs: cadfs__00826947, cadfs__00830309, cadfs__00984691

## Operation errors

| Error | B0 | M2 |
|---|---:|---:|
| Missing | 4 | 2 |
| Extra | 1 | 0 |
| Wrong type | 3 | 0 |
| Wrong order | 0 | 0 |

## Parameter and taxonomy

- Placement paired N=59; B0 median=0.0; M2 median=0.0.
- M2 placement-tag cases=21; feature-tag cases=22; curve-tag cases=23.
- Structure-correct/geometry-wrong cases=22; placement support=19/22.

## WHAT vs WHERE

C2 input is curve-local XYZ + unchanged tangent basis + normalized abscissa, with a separate log-length scale branch. It does not explicitly carry global center, placement plane/axis, parent surface, profile membership, or curve order. The 8 learned-query cross-attention summary also has no positional or relation encoding. This is consistent with, but by itself does not prove, the WHAT-over-WHERE hypothesis.

## Method V2 (not implemented)

NEXT_METHOD_CHANGE = PLACEMENT_AWARE_CURVE_TOKEN
MINIMAL_CHANGE = Fuse each frozen C2 local token with global curve centroid, bbox/extent, valid global endpoints, and global plane normal/principal orientation through one small MLP; keep the 8-query summary unchanged.

All other variables remain frozen for attribution.
