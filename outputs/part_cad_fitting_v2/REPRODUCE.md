# PART_CAD_FITTING_V2

The frozen experiment contains the original 20 objects and 209 P3 parts, including 153 major parts. No segmentation, training, normalization changes or reassembly are performed.

## Resume on the original server

Run `/data/miniconda3/envs/cadfit-env/bin/python -B /data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_fitting_v2/scripts/run_part_cad_fitting_v2.py`.

Completed case results and candidate records are reused. The preparation script refuses to overwrite an existing manifest. The reviewed Near gate records the low rescue rate and its analysis before Reject fitting. For an independent reproduction, use an isolated output copy, update the preparation destination explicitly and retain the frozen source paths and seeds. Never delete the original V1 or protected historical files.

`reports/summary.json` contains final outcome counts. `tables/part_v1_v2_comparison.csv` is the paired comparison; `cases/*/*/candidates` contains every attempted native program, parameters, execution record and available metrics. Optimization proxy traces and final evaluated summaries are separate. Candidate 0 reimports the original STEP and rescores its frozen tessellation; new candidates execute native CadQuery, export and reload STEP before evaluation.

`integrity/VALIDATION.json` records protocol checks; `integrity/READ_ONLY_GUARD.json` checks original protected file hashes and mtimes. Nine optimizer state files were separately deleted with explicit user authorization before this guard was established; model weight files were retained. That storage cleanup is not a CAD pipeline operation.

At most eight candidates per part, including baseline, are executed. Acceptance retains the original 20,000-point and IoU128 evaluator. Proxy optimization is not the acceptance evaluator. Geometry hypotheses and family assignments are deterministic reconciliations under an assistant-authored batch policy; separate per-part LLM API calls are not claimed. The implementation does not include arbitrary CSG search or connected frame-graph decomposition.

Visualizations compare source, V1 and V2 under one camera and scale per part. If fewer than ten Near rescues exist, every actual rescue is shown and the shortfall is stated. No successful example is fabricated.

An intermediate NumPy scalar serialization defect was repaired without changing candidate IDs or fitted parameter values. Files named `before_numeric_repair` and directories named `pre_numeric_repair` are obsolete audit evidence, not current candidates or final results. See `reports/NUMERIC_SERIALIZATION_REPAIR.md`. Only active `record.json`, per-case `result.json`, `cad/` and the final tables describe current selections.
