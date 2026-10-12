# Exp1 Failure / Symmetry / Part Audit

## CURRENT_GATE
- **EXP1_PART_LEVEL_GENERALIZATION_FAIL**

### Sub-gates
- EXP1_RECON_MECHANISM = **PASS**
- EXP1_MEDIAN_GEOMETRY = **PASS**
- EXP1_BASELINE_IMPROVEMENT = **PASS**
- EXP1_PART_GENERALIZATION = **FAIL**

- test CD mean/median = `7.4431e-02` / `7.8351e-03`
- part-macro CD = `5.0982e-01`
- vs mean-baseline = `0.1085`

## 1. Per-part test metrics

| part_id | #patches | CD mean | CD median | HD95 | ctrl L1 | worst CD | dense/patch diag |
|---|---:|---:|---:|---:|---:|---:|---:|
| `23471_3dafd9b1_0001` | 4 | 1.5533e+00 | 1.5856e+00 | 1.6426e+01 | 1.8204e+00 | 2.1428e+00 | **1.01** |
| `69058_b038ab52_0000` | 4 | 9.4097e-01 | 9.3546e-01 | 8.4066e+00 | 1.0776e+00 | 1.1510e+00 | **1.00** |
| `111226_5fd0c97f_0000` | 7 | 5.4037e-01 | 1.1592e-01 | 2.7178e-01 | 6.9870e-01 | 1.6432e+00 | **1.00** |
| `23597_a3b9f8db_0000` | 28 | 8.6831e-03 | 8.4241e-03 | 1.7925e-02 | 3.9772e+00 | 1.3320e-02 | 25.96 |
| `23742_1df7b245_0000` | 63 | 7.9166e-03 | 7.5625e-03 | 1.6664e-02 | 4.1698e+00 | 1.1393e-02 | 28.33 |
| `23437_a9fd0e5c_0000` | 99 | 7.6442e-03 | 7.5591e-03 | 1.5522e-02 | 4.6973e+00 | 1.3595e-02 | 31.94 |

**结论：你的 micro/macro 分裂完全成立。**

- 190 patches 来自 3 个「好」part → CD ≈ 0.008
- 15 patches 来自 3 个「灾难」part → CD ≈ 0.54–1.55
- micro 被好 part 拉低；macro 被坏 part 拉爆

## 2. Control-grid symmetry — **未解释 ctrl L1**

| metric | value |
|---|---:|
| CTRL_L1_RAW mean / median | **4.1735 / 4.3097** |
| CTRL_L1_SYMMETRY_MIN mean / median | **4.1705 / 4.3096** |
| raw/sym ratio | ≈ **1.004** |
| frac best≠identity | 0.273 |
| among CD&lt;0.02: raw / sym | 4.416 / 4.415 |

8 种 UV orientation（flip / transpose）**几乎不降低** ctrl L1。

因此：**高 ctrl L1 的主因不是离散 U/V 编号歧义。**

### 真正相关的现象（好例上）

在 CD_rel &lt; 0.02 的 190 个 patch 上（local frame）：

| | mean |
|---|---:|
| GT pole RMS | **10.82** |
| Pred pole RMS | **5.44** |
| GT densified surf RMS | **10.08** |
| Pred densified surf RMS | **3.32** |
| ctrl L1 | **4.42** |

输入点按 **trimmed patch** 的 centroid / bbox-diag 归一化（应 ≈ 单位框），但 densified GT/poles 的 RMS 仍是 ~10——说明 **loss 监督的曲面域和输入点域不是同一个东西**。

## 3. 根因：`dense/patch` 域不匹配（比 UV symmetry 更关键）

Exp1 densify 用的是 canonical 4×4 在 **完整 UV∈[0,1]** 上的 evaluate（未按 trim 限制）。

| split | dense_diag / patch_diag |
|---|---|
| train median / p95 | **42.1 / 50.8** |
| train frac &gt; 5 | **86.4%** |
| test **好** parts median | **26–32** |
| test **坏** parts median | **≈1.00** |

例子：

| sample | patch_diag | dense_diag | ratio |
|---|---:|---:|---:|
| `23437_...face_0000`（好） | 1.14 | 35.57 | **31.3** |
| `23471_...face_0002`（坏） | 749.4 | 756.7 | **1.01** |
| `111226_...face_0012`（坏） | 23.3 | 23.5 | **1.01** |

解释：

1. 训练主体 = 小 trim 贴在巨大未裁剪 sheet 上。
2. 归一化用 patch 尺度，但 `L_surf` / metrics 用整张 sheet → 模型学的是「大 sheet 坐标系下的平均 strip」。
3. 三个坏 part 恰好是 **trim ≈ 全参数域**（ratio≈1）→ 归一化语义正确 → 训练学到的偏差直接暴露 → CD 爆炸（pred scale_ratio ≈ 30×）。
4. 三个好 part 的「低 CD」很大程度是 **在错误的大 sheet 域上自洽**，不能当作真正的 trim-face reconstruction PASS。

**所以：EXP1_MEDIAN_GEOMETRY / MECHANISM 的 PASS 需要降级解读**——median 好看，但监督域有 bug；part-level FAIL 才是真实信号。

## 4. Worst-20 failure types（修正标签）

自动启发式原先大量标成 `TRANSLATION_ERROR`；结合域审计后，灾难例更应理解为：

| 修正类型 | 含义 | 典型 |
|---|---|---|
| **DOMAIN_MISMATCH_SCALE** | 模型输出训练态大 sheet；GT 是单位化真 patch | 坏 part 的 CD&gt;0.2 共 11 个 |
| **STRIP_OOD** | degree 5×1 + 高 poles_u + 高 aspect | 坏 part 全部 `5x1`；train 多为 `3x1`/`5x2` |
| OTHER（CD≈0.01 的「worst」尾） | 好 part 内部相对较差，但仍远好于坏 part | 不应当灾难例 |

Worst-20 里 CD&gt;0.2 的 11 个 **全部** 来自三个坏 part，且 `dense/patch≈1`。

情况归类（对照你的 A/B/C/D）：

- **情况 A（UV 反了）**：symmetry audit **不支持**作为主因（sym≈raw）。
- **情况 B（位置/尺度）**：**主因**——但根子是 densify 域 / 归一化不一致，不是简单 inverse-transform 写错一行。
- **情况 C（端部翘起 → 支持 Exp2 Boundary）**：**目前没有干净证据**；先修域再谈 Boundary。
- **情况 D（塌成平均 strip）**：坏 part 上成立（pred 保持 train 态大 RMS）。

## 5. Train vs bad-part 分布（OOD）

| | train | test good parts | test bad parts |
|---|---:|---:|---:|
| PCA aspect median / p95 | 1.50 / 5.87 | 1.49 / 2.62 | **6.24 / 15.62** |
| degree | 3×1:273, 5×1:29 | mostly strip-like | **全部 5×1 (15)** |
| poles | 多为 **5×2** | 类似 | **15×2…68×2**（长 strip） |
| dense/patch | median **42** | **26–32** | **≈1** |

坏 part 同时踩中：

1. 更高 aspect（更细长）
2. native `5×1` + 更多 poles_u
3. **唯一** `dense/patch≈1` 的 held-out 几何

## 6. Gate 重命名（已写入 REPORT）

```
EXP1_RECON_MECHANISM=PASS          # 相对 mean-baseline 大幅下降（需带域 caveat）
EXP1_MEDIAN_GEOMETRY=PASS          # median CD 低（同 caveat）
EXP1_BASELINE_IMPROVEMENT=PASS
EXP1_PART_GENERALIZATION=FAIL

CURRENT_GATE=EXP1_PART_LEVEL_GENERALIZATION_FAIL
```

额外建议加一条工程 gate（尚未改代码）：

```
EXP1_SUPERVISION_DOMAIN_CONSISTENT = FAIL
```

因为 train 86% 的 densified GT 比 patch 大 5× 以上。

## 7. 下一步（按你选的 audit_only，不重训）

修 Exp1 监督域后再谈 λ_ctrl_sym / λ_ctrl=0：

1. densify / CD 只在 **trimmed UV bbox**（或 face 采样点）上算；或
2. 用 densified GT 自己的 centroid/diag 做 frame；或
3. 直接对 trimmed surface samples 做 LSQ 4×4（canonical 已是 LSQ，但 evaluate 域要 trim-aware）

在域修干净之前：

- **不要**把 median CD=7.8e-3 当成 trim-face 重建已成功
- **不要**上 Exp2 Boundary（否则会继续在错误监督上叠加变量）
- UV symmetry loss **可以做**，但预期对当前 ctrl=4.17 **帮助很小**

Artifacts: `per_part_test.json`, `symmetry_audit.json`, `worst20.json`, `ood_distribution.json`, `per_sample_audit.json`
