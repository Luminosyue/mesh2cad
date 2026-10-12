# OVERFIT10

Seed=42. 10 CAD: 未截断、EOS 完整、GT STEP reload 成功、M2 全序列 ≤1024。

IDs: `deepcad__0052_00522845` (Box), `0097_00970426` (Box+Union), `0054_00542661` (Circle+Cut), `0043_00438809` (Polygon+Cut), `0060_00601219` (multi-op), `0005_00051866` (Box), plus 4 短样本。

协议：fresh BASE_MODEL，lr=2e-5，AdamW，禁止 silent truncate。Sonata/point_proj 冻结。M2 用当前 frozen C2，不是 Dora。

| arm | epoch | train CE | exact | EOS | parse | STEP |
|---|---:|---:|---:|---:|---:|---:|
| TEXT identical instruction | 80 | 0.0204 | 0.10 | 1.00 | 1.00 | 1.00 |
| TEXT + CAD_ID | 25 | 0.0007 | **1.00** | 1.00 | 1.00 | 1.00 |
| SURFACE-ONLY (B0) | 25 | 0.0021 | **1.00** | 1.00 | 1.00 | 1.00 |
| M2 | 25 | 0.0001 | **1.00** | 1.00 | 1.00 | 1.00 |

相同 instruction、没有 CAD_ID 时 greedy 只能解出一种程序，exact 卡在 1/10，但 EOS/STEP 已是 100%。加上 CAD_ID 后 25 epoch exact=10/10。

B0 与 M2 不需要 CAD_ID，表面点云已足够区分 10 个样本。

结论：Case 4。SFT / splice / M2 fusion 在干净短样本上可以过拟合。不要把 800 训不满归咎于 labels 或 M2。
