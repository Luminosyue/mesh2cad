# Native parametric CAD audit V1

Start with reports/FINAL_REPORT.md and reports/SUMMARY.json. V1 = original 209; V3 = current 209, kept separate. Gallery: visualizations/index.html. The synthetic faceted control is excluded from dataset counts.

Reproduction (server, original inputs required):
1. Run scripts/run_audit.py using /data/miniconda3/envs/cadfit-env/bin/python -B (completed case audits are resumed).
2. Run scripts/test_validator.py.
3. Run scripts/render_surface_audit.py.
4. Run scripts/run_audit.py --guard-after.
5. Run scripts/finalize_audit.py, then scripts/package_audit.py.

Use a fresh audit output directory for a new independent run; root paths in run_audit.py are pinned to this dataset. No historical pipeline scripts are modified. Existing isolated execution artifacts are evidence; no historical STEP exports are overwritten.

Standalone validation: python -B scripts/validate_native_parametric_cad.py --cad INPUT/cad.py --step INPUT/cad.step --source-mesh INPUT/part_local.ply --out NEW_AUDIT/case.json
Exit 0 = A representation acceptance; 2 = nonaccepted; other failures = nonzero. This validator must be explicitly invoked in future generation; it is not retroactively wired into read-only historical pipelines.

Representation PASS does not change geometric status or admit all 209 as high-quality training pairs.
