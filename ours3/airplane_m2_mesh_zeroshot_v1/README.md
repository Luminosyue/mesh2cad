# Airplane mesh-derived curve zero-shot stress test

**Not a formal main result.** M2 was trained mostly on B-Rep oracle curves;
airplane inputs use mesh sharp-edge → fitted curves (domain shift).

- Source: X-Part 9/9 watertight (`airplane_p3_xpart_cadfit_routea_v1`), no P3/X-Part re-run
- Surface: 4096 xyz+normal, target_diagonal=6 canonical
- Curves: 30° sharp → GT-free chains → fit LINE/CIRCLE/ELLIPSE/BSPLINE → C2 tokens (cap 128)
- Models: heldout last ckpts `heldout_curve_{b0,m2}_s0`
- Metrics: mesh-reference only (no GT DSL)

Artifacts: `parts/`, `decode/`, `metrics/`, `viz/`, `assembly/`, `TABLE_ALL9.md`
