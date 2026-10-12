# Multi-case Mesh-to-CAD MVP

This extension runs six controlled cases through the same pipeline:

1. `rotated_shelf`: five rotated/axis-aligned boxes — expected pass.
2. `tilted_stool`: one box and three tilted elongated cylinders — expected pass.
3. `pipe_rack`: two boxes and three cylinders with different axes — expected pass.
4. `wheeled_cart`: two boxes and four short/wide wheel cylinders — stress case for the PCA classifier.
5. `dumbbell`: one elongated cylinder and two short/wide cylinder plates — stress case.
6. `unsupported_mixed`: box, elongated cylinder, sphere and cone — unsupported-type failure case.

## Run Mesh recognition and geometric evaluation

```bash
python run_batch_cases.py
```

Outputs are placed in `outputs_batch_cases/<case_id>/`:

- `01_input_highpoly.{ply,obj}`
- `02_lowpoly.{ply,obj}`
- `part_*.ply`
- `primitives.json`
- `03_parametric_reconstruction.{ply,obj,scad}`
- `metrics.json`
- `preview_*.png`

Batch summaries:

- `outputs_batch_cases/batch_summary.csv`
- `outputs_batch_cases/batch_summary.json`
- `outputs_batch_cases/batch_contact_sheet.png`

## Export STEP in CadQuery/OCP environment

```bash
python export_steps_batch.py
```

This writes `outputs_batch_cases/<case_id>/model.step` for every case. The current recognizer always emits only `box` and `cylinder`, so STEP export will succeed even for stress cases, but sphere/cone and short-cylinder parts may be exported as incorrect boxes. Geometry metrics and type accuracy must therefore be checked before treating an output as a valid reconstruction.

## Main conclusion

The current rule system generalizes to rotated boxes and elongated cylinders, including tilted axes. It fails systematically on short/wide cylinders because PCA's largest eigenvector is no longer the cylinder axis. It cannot represent sphere or cone and approximates both as boxes. These failures identify the next implementation priority: replace the binary PCA rule with analytic primitive fitting and model selection for box, cylinder, sphere, cone and possibly torus.
