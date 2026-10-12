# Exp1 PointNet Surface-only Reconstruction (4×4 LSQ)

- CURRENT_GATE = **EXP1_PART_LEVEL_GENERALIZATION_FAIL**
- EXP1_RECON_MECHANISM = **PASS** (caveat: densify domain)
- EXP1_MEDIAN_GEOMETRY = **PASS** (caveat: densify domain)
- EXP1_BASELINE_IMPROVEMENT = **PASS**
- EXP1_PART_GENERALIZATION = **FAIL**
- EXP1_SUPERVISION_DOMAIN_CONSISTENT = **FAIL** (train median dense/patch diag ≈ 42)
- test chamfer_rel mean/median = **7.4431e-02** / **7.8351e-03**
- test part-macro chamfer_rel = **5.0982e-01**
- CTRL_L1_RAW mean = **4.1735**
- CTRL_L1_SYMMETRY_MIN mean = **4.1705** (≈ raw → UV flip 不是主因)
- vs mean-baseline ratio = **0.1085**

Per-part / symmetry / worst / OOD / domain audit: `audits/AUDIT.md`
