# TRAINING_DATA_AUDIT_V1

- CURRENT_GATE = **TRAINING_DATA_AUDIT_V1_PASS_WITH_WARNINGS**

### Sub-gates
- CAD_LEVEL_SPLIT = **PASS**
- NO_STEP_SHA_CROSS_SPLIT = **PASS**
- GEOMETRY_ONLY_INPUT_CONTRACT = **PASS**
- TYPE_BALANCE = **WARN**
- CIRCLE_SPLIT_SKEW = **PASS**
- ELLIPSE_SAMPLE_SIZE = **WARN**
- CAD_DIVERSITY = **WARN**

## Verdict (data construction vs training risk)

| axis | status |
|---|---|
| 几何正确性 | ✅ (prior validation; not re-litigated) |
| 参数完整性 | ✅ |
| 拓扑完整性 | ✅ |
| Track A 隔离 | ✅ |
| 类别平衡 | ⚠️ LINE=95.33% majority baseline=95.3% |
| 训练/推理输入一致性 | ✅ Geometry-only default |
| split leakage | ✅ CAD/family clean |
| CIRCLE split skew | ✅ |
| CAD diversity | ⚠️ n_CAD=2796 families=2702 |
| Ellipse 样本量 | ⚠️ n=366 |

## 1. CAD-level split

- seed = `42`
- CAD counts = `{'train': 2231, 'val': 280, 'test': 285}`
- families = `2702`
- leak items = **0**

## 2. Type imbalance

- TOTAL_CURVES = **172622**
- majority = **LINE** (95.33%)
- majority-class baseline accuracy = **0.9533**

| type | count | % |
|---|---:|---:|
| LINE | 164564 | 95.33% |
| CIRCLE | 6127 | 3.55% |
| ELLIPSE | 366 | 0.21% |
| BSPLINE | 1565 | 0.91% |

### Per-split curve distribution

| split | n_curves | LINE% | CIRCLE | ELLIPSE | BSPLINE | CIRCLE-CAD frac |
|---|---:|---:|---:|---:|---:|---:|
| train | 139020 | 96.18 | 4518 | 209 | 581 | 0.323 |
| val | 16003 | 93.18 | 518 | 121 | 452 | 0.379 |
| test | 17599 | 90.57 | 1091 | 36 | 532 | 0.365 |

## 3. Duplicate / near-duplicate

- unique STEP sha256 = **2795**
- sha collision groups (same STEP, different cad_id) = **1**
- sha cross-split = **0**
- fingerprint cross-split = **39**
- Fusion multi-body families = **72**
- examples sha collisions = `[{"sha256": "7ae73a2e92e59530\u2026", "keys": ["deepcad_train/0051_00514163", "deepcad_train/0099_00997649"]}]`

## 4. Length / span / BSpline tail

- length_world decades_span = **11.538635324435884** (min=7.936374402106594e-08, max=27432.0)
- length_normalized median/p95 = **0.36133238673210144** / **9.027935981750488**
- curve_u_span median/p95 = **0.08361111591170162** / **7.000000000000398**
- CIRCLE arc_deg median = **269.98874122664097**
- ELLIPSE arc_deg median = **7.8913722991856865**
- BSPLINE ncp median/max = **10.0** / **95.0** degree=`{'6': 1, '4': 3, '5': 102, '8': 2, '7': 2, '3': 1455}`

## 5. Input contract (train ↔ mesh/Dora inference)

- primary recommended input = `xyz_normalized + tangent + curve_u`
- current B1 = `xyz_normalized + tangent`
- curve_u missing in B1 = **True**
- FORBIDDEN as primary input = `['GT curve_type', 'GT center / radius / normal / control_points', 'world-space raw length as continuous feat without log/norm']`
- supervision OK = `['curve_type', 'normalized parametric parameters', 'xyz reconstruction on sample grid']`

## 6. CAD diversity

- n_CAD = **2796** (DeepCAD 2194 + Fusion360 602)
- families = **2702**
- CADs with BSPLINE = **51**
- curves/CAD median = **23.0**

172k curves look large but sit on 2796 CAD objects, ~95% LINE. Fine for single-curve encoder; weak for proving complex freeform CAD generalization. If target domains include aerospace/robotics/organic assets, add freer-form CAD later.

## Actions before CURVE_ENCODER_BASELINE_V1

1. **Do not rebuild** the 832MB curve GT pack (no construction bug found).
2. If `CIRCLE_SPLIT_SKEW=FAIL`: fix `splits.py` rarity sort (do not prefer CIRCLE into val/test), regenerate CAD-level split.
3. Train with class weights and/or oversample ELLIPSE/BSPLINE; **keep test natural**.
4. Encoder input = sampled xyz[+tangent][+curve_u]; never GT type/params.
5. Use normalized / log length — not world raw length.
6. Treat joint Surface→DSL freeform coverage as orthogonal (DSL has no BSpline ops).

