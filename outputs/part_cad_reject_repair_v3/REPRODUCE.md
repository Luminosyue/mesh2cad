# Reject CAD Repair V3

Server output: `/data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_reject_repair_v3`.

Run `/data/miniconda3/envs/cadfit-env/bin/python -B /data/home/cuiyuehan/project/mesh2cad/outputs/part_cad_reject_repair_v3/scripts/v3_run.py --workers 12` to resume fitting. Completed per-case results and candidate records are reused. Run `v3_finalize.py`, then `v3_visualize.py` using the same interpreter and script directory to rebuild reporting and validation. `v3_package.py` freezes the delivery only after validation passes.

Only V2 Reject cases are fitted. V2 Strict and Near CAD files are copied exactly. Do not edit or rerun V2 in its existing output directory. `v3_prepare.py` refuses to overwrite an existing manifest. Independent reproduction requires an isolated output copy, adjusting only the preparation destination, and the original V2 input directory kept read-only. Review the pilot before proceeding through the full cohort. All actual fitting paths derive from the new script directory.

Acceptance uses the unchanged V2 metric implementation/configuration and original source/CAD sample seeds. Proposal selection uses approximate analytic meshes, 4000-point subsets and a coarse voxel proxy; these are not final CAD or acceptance metrics. Native programs only use bounded CadQuery primitives, sketches, lofts, revolutions and Booleans. No source mesh is imported into CAD. The proposal pool can contain more hypotheses than the seven native candidates executed per part; all proposal descriptions and proxy scores are retained. Eight evaluated candidates include the V2 baseline.

`optimization/proposals.json` records geometry hypotheses, selections, generation failures and local search steps. `candidates/*/record.json` records native execution and exact protocol metrics. `optimization/final_summary.json` identifies initial/best numeric parameters and scores. `tables/part_v2_v3_comparison.csv` includes all 209 parts; `tables/reject_recovery.csv` contains the 124-case repair cohort.

The selected baseline reimports STEP and rescores the frozen STEP-derived mesh, preserving tessellation/sample ordering. Preserved non-Reject execution results are inherited from V2 and file hashes are verified. Numerical Strict acceptance does not prove perfect topology or every small detail. No reassembly, training or additional object selection is part of this run.
