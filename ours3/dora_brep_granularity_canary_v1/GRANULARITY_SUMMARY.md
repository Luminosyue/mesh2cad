# Dora / BRep granularity canary V1

Question: is rare fitted ELLIPSE / BSPLINE UNMATCHED mainly from Dora-chain granularity != single GT BRep edge granularity?

**Answer (analysis-only, 10 frozen visual cases):** mostly yes for DeepCAD; the two Fusion360 cases are fitted-type false positives with no nearby GT geometry.

- TOTAL_CASES: 10
- SINGLE_GT_EDGE_COMPATIBLE: 0
- MULTI_GT_SAME_PRIMITIVE: 0
- MULTI_GT_HETEROGENEOUS_PRIMITIVES: 8
- FITTED_TYPE_FALSE_POSITIVE: 2
- NO_REASONABLE_GT_GEOMETRY: 0
- AMBIGUOUS: 0

The 8 MULTI_GT cases are a single Dora chain covering a connected union of multiple GT LINE edges (not one analytic ELLIPSE/BSPLINE, and not one collinear LINE). Single-edge Dora→GT coverage is ~0.23–0.64; the connected edge-set union reaches 1.0 / 1.0. Example: `deepcad__0039_00394545` chain 15 is LINE→LINE at a corner; several ELLIPSE fits are long polylines tessellated into 17–32 GT LINE edges.

The 2 FITTED_TYPE_FALSE_POSITIVE cases (Fusion360) have ~0 coverage even against the connected nearby set.

Formal MATCH_CLASS, correspondence, thresholds, Dora, chain extraction, fitting, and C2 were not modified.

| CAD_ID | type | MATCH_CLASS | label | single d2g/g2d | set d2g/g2d | GT set |
|---|---|---|---|---|---|---|
| deepcad__0098_00987776 | ELLIPSE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.277/1.000 | 1.000/1.000 | 17× LINE |
| deepcad__0028_00283333 | ELLIPSE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.359/1.000 | 1.000/1.000 | 32× LINE |
| deepcad__0030_00305050 | ELLIPSE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.230/1.000 | 1.000/1.000 | 17× LINE |
| fusion360__40705_5ff43505_0036 | ELLIPSE | UNMATCHED | FITTED_TYPE_FALSE_POSITIVE | 0.000/0.000 | 0.000/0.000 | LINE |
| deepcad__0035_00359126 | ELLIPSE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.309/1.000 | 1.000/1.000 | 17× LINE |
| deepcad__0084_00840479 | BSPLINE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.230/1.000 | 1.000/1.000 | 32× LINE |
| deepcad__0039_00394545 | BSPLINE | PARTIAL | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.637/1.000 | 1.000/1.000 | LINE -> LINE |
| deepcad__0099_00990492 | BSPLINE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.301/1.000 | 1.000/1.000 | 32× LINE |
| fusion360__24927_543d2801_0000 | BSPLINE | UNMATCHED | FITTED_TYPE_FALSE_POSITIVE | 0.000/0.000 | 0.000/0.000 | LINE |
| deepcad__0056_00569646 | BSPLINE | UNMATCHED | MULTI_GT_HETEROGENEOUS_PRIMITIVES | 0.266/1.000 | 1.000/1.000 | 63× LINE |
