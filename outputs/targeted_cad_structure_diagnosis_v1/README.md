# TARGETED_CAD_STRUCTURE_DIAGNOSIS_V1

Frozen pilot: 20 Near + 15 Extrude+Cut + 10 Simple Primitive, 45 distinct cases.
All 76 Near receive metadata-only gate decomposition. All 61 Extrude+Cut and 47 Simple Primitive receive read-only residual/cut-ablation/section audits. Only the 45-case pilot generates new CAD.

Main entry: `scripts/run_structure_diagnosis.py`.

Server runtime: `/data/miniconda3/envs/cadfit-env/bin/python -B`.
Working directory: `/data/home/cuiyuehan/project/mesh2cad/outputs/targeted_cad_structure_diagnosis_v1`.

Run order on a newly prepared output directory:

```sh
python -B scripts/prepare_structure.py
python -B scripts/test_structure.py
python -B scripts/run_structure_diagnosis.py --phase audit --workers 8
python -B scripts/section_audit.py
python -B scripts/run_structure_diagnosis.py --phase pilot --workers 12
python -B scripts/prepare_structure.py --verify
python -B scripts/semantic_feature_review.py
python -B scripts/report_structure.py
python -B scripts/visualize_structure.py
python -B scripts/validate_delivery.py
python -B scripts/package_delivery.py
```

Preparation intentionally refuses to overwrite an existing manifest. Completed pilot cases and candidate records are reused on resume. To reproduce from scratch, use a separate new output directory with the same read-only sibling historical inputs; never delete or overwrite historical CAD.

Source meshes, transforms, provenance and 20,000 cached evaluation points are copied unchanged. CAD sampling uses the original deterministic seed. Candidate STEP is independently re-executed and validated, then reloaded and tessellated with the original evaluation tolerances; the serialized PLY is the evaluated mesh. Display figures do not change evaluation meshes.

`factory_config.json`, `metric_runtime.py`, `fit_logic.py` and `historical_fit.py` are inherited evaluator dependencies. Their legacy driver metadata/functions are not executed. The active task configuration is `config/structure.json`. No Smoke100, P3, training, reassembly, or assembly-render job is launched.

Read `reports/SUMMARY.json`, `reports/FINAL_READOUT.txt`, six reports, `tables/feature_type_success.csv` and `visualizations/index.html` together. Rule-supported feature labels are hypotheses, not independent semantic ground truth. A successful Boolean edit can be an end trim rather than a real pocket/hole; candidate acceptance is not semantic detector precision.
