# FREEFORM_PATCH_RECONSTRUCTION_V1

Minimal closed loop:

```text
1024×6 Patch Points
    → Surface Encoder
    → Latent
    → Surface Decoder
    → Canonical Control Grid
    → B-Spline Surface
```

## Status

| Stage | Result | Path |
|---|---|---|
| Canonical **true LSQ** 4×4 fit gate | **PASS** | `cad_spatial_dataset/Fusion360/freeform_surface_pack_v1/canonical_4x4_fit_gate.md` |
| Exp0 type probe | **PASS** (PointNet, CPU) | `ours3/freeform_patch_reconstruction_v1/exp0_type_probe/` |
| Exp1 BSpline recon | next | **4×4 LSQ poles**, PointNet, surface-only, online resample |

## CANONICAL_4X4_FIT_GATE (true fit, not UV-as-poles)

```text
Original BSpline → 32×32 UV samples → LSQ cubic 4×4 poles → re-evaluate → CD/HD vs GT
```

Frozen:

```text
CANONICAL_GRID=4x4
DEGREE_U=3
DEGREE_V=3
representation=lsq_cubic_clamped_open
```

`canonical_surface.npz` has been **rewritten** for all 729 faces with fitted poles.

## Exp0 type probe (PointNet stand-in; no GPU for Sonata)

```text
overall accuracy = 0.866
BSpline precision = 0.890
BSpline recall    = 0.907
BSpline F1        = 0.899
GATE = EXP0_TYPE_PROBE_PASS
```

Confusion (test):

| GT \ Pred | PLANE | CYLINDER | BSPLINE |
|---|---:|---:|---:|
| PLANE | 155 | 10 | 23 |
| CYLINDER | 4 | 21 | 0 |
| BSPLINE | 7 | 12 | 186 |

Patch geometry **does** carry surface-type signal. Re-run with `--encoder sonata` when CUDA is available before claiming Sonata specifically works.

## Exp1 plan (next)

```text
Input:  patch_points [1024,6]
Output: poles [4,4,3]  (=16×3)
Loss:   L = L_ctrl (L1) + L_surf (Chamfer on densified surfaces)
Metrics: ctrl L1, Chamfer, Hausdorff95, Normal consistency + overlay preview
```

Commands:

```bash
# audit (done)
python3 scripts/freeform_patch_reconstruction_v1/canonical_grid_audit.py

# exp0 (done on CPU PointNet)
python3 scripts/freeform_patch_reconstruction_v1/exp0_type_probe.py --encoder pointnet

# exp0 with Sonata (when GPU up)
python3 scripts/freeform_patch_reconstruction_v1/exp0_type_probe.py --encoder sonata --device cuda
```
