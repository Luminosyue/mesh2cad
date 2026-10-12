# PART_CAD_FITTING_V2_NATIVE_AND_RENDER_V4

Read part_cad_fitting_v2_native/reports/PART_CAD_FITTING_V2_NATIVE_REPORT.md and reports/SUMMARY.json. Original V1 is the paired 4/63/142 reference. Prior V3 improvements are preserved and separately attributed; this round is not a relabeling of those gains.

Fitting entry: scripts/run_part_cad_fitting_v2_native.py --phase near --workers 12; only after reports/NEAR_GATE.json permits it, use --phase reject --workers 12. Candidate jobs resume completed records. All final geometry gates use frozen original source/seed/evaluator. Numerical proposals and proxy search traces are retained.

Renderer entry: cad_render_v4/scripts/render_v4_assemblies.py. Run under xvfb-run with TMPDIR set to cad_render_v4/runtime. It renders unchanged historical V3 STEP, not newly fitted outputs, so display improvements are isolated from geometry improvements. Evaluation tessellation is never replaced with display tessellation.

Environment: /data/miniconda3/envs/cadfit-env/bin/python -B on the original server. Dependencies: CadQuery/OCP, NumPy, scipy, shapely, trimesh, VTK, Pillow and Xvfb. Paths are pinned to the original dataset. Input copies and selected native programs are included. Running preparation again in a completed output directory is intentionally refused.

Validation scripts: test_native_profiles.py; prepare_native_v2.py --verify (historical hashes); report_native_v2.py; visualize_native_v2.py under Xvfb; validate_native_v2_delivery.py. Never overwrite the historical V1/V2/V3/audit directories. No training, scale-up, source change, P3 rerun or assembly optimization was performed.

Open cad_render_v4/index.html for 20 unchanged-geometry V3/V4 render comparisons. Open part_cad_fitting_v2_native/visualizations/index.html for 30 source/V1/new CAD/overlay comparisons. Each category is labeled; inherited rescues are not claimed as new.
