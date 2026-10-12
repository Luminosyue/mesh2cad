# C2 epoch 4 权威评测报告

本报告只使用 provenance 已核对的 C2 checkpoint，不沿用旧 D1/C2 混乱结果。

## Provenance

- checkpoint: `ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt`
- sha256: `553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9`
- best_epoch: **4**
- frozen: `True`
- spec: curve-local + log-length scale branch
- token: fused 256-D (`out['token']`), 即送给 SpatialLM 的向量

## Test 1 — Intrinsic classification

- n_curves = 17147
- support: {'LINE': 16486, 'CIRCLE': 503, 'ELLIPSE': 26, 'BSPLINE': 132}

| type | precision | recall | F1 | support |
| --- | ---: | ---: | ---: | ---: |
| LINE | 0.9959 | 0.9960 | 0.9960 | 16486 |
| CIRCLE | 0.9307 | 0.8807 | 0.9050 | 503 |
| ELLIPSE | 0.0441 | 0.1154 | 0.0638 | 26 |
| BSPLINE | 0.8190 | 0.7197 | 0.7661 | 132 |

- **Macro F1** = 0.6827
- **Micro F1** = 0.9892 （单标签多分类下等于 overall accuracy 0.9892）
- Balanced accuracy = 0.6779

Confusion（行=GT，列=Pred，顺序 LINE / CIRCLE / ELLIPSE / BSPLINE）:

```
[
  [
    16420,
    4,
    56,
    6
  ],
  [
    36,
    443,
    9,
    15
  ],
  [
    3,
    20,
    3,
    0
  ],
  [
    28,
    9,
    0,
    95
  ]
]
```

- **LINE→CIRCLE** = 4  (rate 0.000243)
- **CIRCLE→LINE** = 36  (rate 0.071571)
- **ELLIPSE row** = {'LINE': 3, 'CIRCLE': 20, 'ELLIPSE': 3, 'BSPLINE': 0}
- **BSPLINE row** = {'LINE': 28, 'CIRCLE': 9, 'ELLIPSE': 0, 'BSPLINE': 95}

## Test 2 — Param / Recon geometry

C2 recon is supervised in curve-local frame (center + bbox-extent scale). Param head is supervised in object-normalized analytic param space from frozen_v1 cache.

### LINE
- direction error (deg, unsigned): `n=16486 mean=12.8818 median=7.6969 p90=29.5563 p95=45.9660`

### CIRCLE
- center error: `n=503 mean=27.5760 median=8.0595 p90=46.6980 p95=99.6718`
- normal angular error (deg): `n=503 mean=9.7425 median=5.6283 p90=18.6538 p95=42.4708`
- radius error (abs): `n=503 mean=1.3776 median=0.3216 p90=2.8972 p95=6.0104`
- radius relative error: `n=503 mean=0.2998 median=0.2408 p90=0.6106 p95=0.8792`

### ELLIPSE
- center error: `n=26 mean=2.9506 median=3.3266 p90=4.6170 p95=4.9720`
- major radius abs / rel: `n=26 mean=0.3723 median=0.1800 p90=1.0568 p95=2.0681` / `n=26 mean=1.0476 median=0.4285 p90=2.2564 p95=2.2564`
- minor radius abs / rel: `n=26 mean=0.4834 median=0.2894 p90=1.3752 p95=2.0619` / `n=26 mean=2.4088 median=2.5232 p90=3.6976 p95=3.6976`
- major-axis orientation (deg): `n=26 mean=63.7455 median=74.2846 p90=85.2657 p95=85.2657`
- minor-axis orientation (deg): `n=26 mean=62.7535 median=80.0458 p90=80.2559 p95=80.2559`

### Reconstruction (curve-local frame)
- Chamfer: `n=17147 mean=0.0304 median=0.0216 p90=0.0629 p95=0.0777`
- ordered MSE: `n=17147 mean=0.0044 median=0.0009 p90=0.0064 p95=0.0178`
- ordered RMSE: `n=17147 mean=0.0442 median=0.0294 p90=0.0799 p95=0.1333`

| type | chamfer mean/median/p90/p95 | ordered MSE mean/median |
| --- | --- | --- |
| LINE | 0.0282 / 0.0210 / 0.0564 / 0.0718 | 0.0024 / 0.0008 |
| CIRCLE | 0.0894 / 0.0814 / 0.1326 / 0.1549 | 0.0666 / 0.0423 |
| ELLIPSE | 0.1247 / 0.1421 / 0.1492 / 0.1492 | 0.0556 / 0.0643 |
| BSPLINE | 0.0656 / 0.0457 / 0.1297 / 0.1734 | 0.0120 / 0.0029 |

## Test 3 — Frozen 256-D token probes

C2 全程冻结。Probe 只看 `out['token']`（除非标明 shape_only）。
`length_log_shape_only` 用来检查 scale 是否泄漏进 shape branch：若 disentangle 成功，shape token 不应轻易预测 log(length)。

### type  (token=`token`, n_test=17147)
- **linear** (val-best epoch 20): macro F1=0.6559  micro F1=0.9926  LINE F1=0.998  CIRCLE F1=0.912  ELLIPSE F1=0.000  BSPLINE F1=0.714
  majority baseline macro F1=0.2451 (LINE)
- **mlp2** (val-best epoch 16): macro F1=0.6969  micro F1=0.9942  LINE F1=0.998  CIRCLE F1=0.930  ELLIPSE F1=0.065  BSPLINE F1=0.795
  majority baseline macro F1=0.2451 (LINE)

### length_log  (token=`token`, n_test=17147)
- **linear** (val-best epoch 20): abs `n=17147 mean=0.0683 median=0.0563 p90=0.1282 p95=0.1638`  rel `n=17147 mean=5.4439 median=0.0387 p90=0.2470 p95=0.3686` pearson=0.9990
- **mlp2** (val-best epoch 20): abs `n=17147 mean=0.0131 median=0.0079 p90=0.0294 p95=0.0406`  rel `n=17147 mean=1.4673 median=0.0055 p90=0.0313 p95=0.0596` pearson=0.9999
- mean baseline abs `n=17147 mean=1.6436 median=1.3942 p90=3.0923 p95=3.4710`  rel `n=17147 mean=189.9249 median=0.7558 p90=3.2410 p95=4.8826`

### length_log_shape_only  (token=`shape_h`, n_test=17147)
- **linear** (val-best epoch 20): abs `n=17147 mean=1.5427 median=1.3221 p90=2.9708 p95=3.4208`  rel `n=17147 mean=209.7048 median=0.7042 p90=3.2511 p95=5.0351` pearson=0.3156
- **mlp2** (val-best epoch 19): abs `n=17147 mean=1.3308 median=1.1504 p90=2.5372 p95=3.2876`  rel `n=17147 mean=71.7668 median=0.8120 p90=2.6915 p95=3.9602` pearson=0.5467
- mean baseline abs `n=17147 mean=1.6436 median=1.3942 p90=3.0923 p95=3.4710`  rel `n=17147 mean=189.9249 median=0.7558 p90=3.2410 p95=4.8826`

### radius_circle  (token=`token`, n_test=503)
- **linear** (val-best epoch 20): abs `n=503 mean=2.3811 median=1.2810 p90=5.4942 p95=7.8258`  rel `n=503 mean=12.5765 median=0.4770 p90=8.1052 p95=96.1727` pearson=0.7932
- **mlp2** (val-best epoch 20): abs `n=503 mean=0.9929 median=0.2492 p90=2.5560 p95=5.1094`  rel `n=503 mean=0.3830 median=0.1418 p90=0.8775 p95=1.8598` pearson=0.9299
- mean baseline abs `n=503 mean=5.4355 median=5.2868 p90=10.9630 p95=13.8692`  rel `n=503 mean=19.6175 median=1.8733 p90=24.7760 p95=133.3345`

### direction_line  (token=`token`, n_test=16486)
- **linear** (val-best epoch 16): angular err deg `n=16486 mean=6.7708 median=4.6572 p90=11.8125 p95=16.5091`
- **mlp2** (val-best epoch 13): angular err deg `n=16486 mean=3.3467 median=1.8265 p90=7.3083 p95=10.1263`
- mean baseline angular err: `n=16486 mean=57.6425 median=53.3377 p90=82.0511 p95=85.1267`

## Test 4 — Nearest-neighbor sanity

- gallery=train (135382), query=test (17147), cosine k=5
- overall type_match@1 = 0.9938
- overall type_match@5 any = 0.9953
- overall type_match@5 majority = 0.9935
- nn1 cosine: `n=17147 mean=0.9998 median=1.0000 p90=1.0000 p95=1.0000`

| type | n | type@1 | type@5 any | type@5 maj | nn1 cosine mean | length rel mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LINE | 16486 | 0.999 | 1.000 | 0.999 | 1.000 | 0.019 |
| CIRCLE | 503 | 0.930 | 0.948 | 0.915 | 0.998 | 0.132 |
| ELLIPSE | 26 | 0.115 | 0.115 | 0.077 | 0.992 | 0.102 |
| BSPLINE | 132 | 0.750 | 0.765 | 0.727 | 0.996 | 0.095 |

- CIRCLE nn1 is CIRCLE: 0.930
- CIRCLE nn1 radius rel-err (when neighbor is CIRCLE): `n=468 mean=0.1456 median=0.0378 p90=0.2525 p95=0.3949`

抽样 examples 见 `test4_nn.json`。

## Test 5 — Invariance

- identity vs dataset feature pipeline cosine: `n=670 mean=1.0000 median=1.0000 p90=1.0000 p95=1.0000`

| perturbation | n | fused cosine mean/median/p90 | shape cosine mean/median/p90 |
| --- | ---: | --- | --- |
| translate | 670 | 1.0000 / 1.0000 / 1.0000 | 1.0000 / 1.0000 / 1.0000 |
| rotate | 670 | 0.6205 / 0.7193 / 0.9447 | 0.4428 / 0.5237 / 0.8978 |
| reverse | 670 | 0.9529 / 0.9636 / 0.9940 | 0.8235 / 0.7961 / 0.9900 |
| resample_start_shift8 | 284 | 0.9868 / 0.9968 / 0.9998 | 0.9959 / 0.9986 / 0.9997 |
| scale_x2 | 670 | 0.9755 / 0.9820 / 0.9927 | 1.0000 / 1.0000 / 1.0000 |

设计预期：
- local_frame: center + max-bbox-extent scale; NO rotational canonicalization
- expected_translate: fused and shape tokens ~invariant
- expected_rotate: NOT invariant (orientation is kept in local xyz + object-frame tangents)
- expected_reverse: not guaranteed; s and tangent both flip
- expected_resample_start: PointNet is permutation-invariant but s is arc-parameter; closed curves may move
- expected_scale_x2: shape token ~invariant; fused token should change via log(length)

## 怎么读这些数

- Test 1 只说明 type head。Type 好、Param/Recon 差 → 更像 classifier。
- Test 2 看 param/recon 是否留下几何。
- Test 3 看 **token 本身** 有没有 CAD 几何，不依赖 C2 自己的 head。
- fused token 预测 length 容易是预期内的（scale branch 显式注入了 log-length）。
- shape-only 预测 length 若也很容易，则 shape/scale 分离不干净。
- Test 4 / 5 是 sanity，不是论文主表。

