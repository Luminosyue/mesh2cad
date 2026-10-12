# STEP Export & OCCT Validation

## Environment
```bash
conda activate text2cadquery
```

## Export
```bash
# Base table
python mesh_to_cad_stage1/export_step_cadquery.py \
  --input mesh_to_cad_stage1/outputs/primitives.json \
  --output mesh_to_cad_stage1/outputs/step_single_sample/synthetic_table/model.step \
  --sample-id synthetic_table \
  --metadata mesh_to_cad_stage1/outputs/step_single_sample/synthetic_table/export_metadata.json \
  --validation mesh_to_cad_stage1/outputs/step_single_sample/synthetic_table/validation.json

# Multi-case batch
python mesh_to_cad_stage1_多案例扩展/mesh_to_cad_stage1/export_steps_batch.py

# Tank
python mesh_to_cad_stage1_坦克复杂组合体/mesh_to_cad_stage1/export_steps_batch.py
```

## Validate
```bash
python validate_step_outputs.py
```

Outputs: `step_validation_summary.json`, `step_validation_summary.csv`

## Notes
- Units match `primitives.json` (same numeric contract as Mesh stage; STEP writer may label mm but values are not scaled ×1000).
- Misrecognized primitives (short cylinders→Box, Sphere/Cone→Box) are exported as recognized; see `known_recognition_errors` in the JSON.
- Multi-part strategy: CadQuery Assembly, no Fuse.
