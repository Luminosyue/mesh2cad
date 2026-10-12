from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3'); O=B/'baseline_comparison_closeout_v1'; C=B/'cadfit_val1000_baseline_v1'
(O/'reports'/'cadfit_recovery_report.md').write_text(f'''# CADFit Recovery Report

- Frozen target manifest: `{C}/provenance/CADFIT_VAL1000_MANIFEST.csv`
- Target cases: 1000 unique IDs.
- Direct frozen source paths present: 253.
- Recovered normalized cache files present: 1000, consisting of 253 existing + 747 recovered entries in `input_recovered_v2_manifest.csv`.
- CADFit prediction/STEP outputs for VAL1000: not found.
- No CADFit inference was started in this closeout; therefore no CADFit metric is reported.

The 1000-file recovered cache is ready for a separate official CADFit input smoke. Until prediction/STEP outputs exist, CADFit is excluded from quantitative full-VAL1000 comparison and must not be labeled as a 253-case result.
''')
(O/'reports'/'cadrille_audit_report.md').write_text('''# Cadrille Audit

No Cadrille directory, checkpoint, repository, inference entrypoint, prediction, or STEP artifact was located under `/data/home/cuiyuehan/project/mesh2cad/ours3`.

No paper/repository, input modality, checkpoint, inference path, output format, or metric row is asserted. Cadrille is excluded until a provenance-qualified artifact is identified.
''')
(O/'reports'/'BASELINE_COMPARISON_SUMMARY.md').write_text('''# Baseline Comparison Summary

Frozen EXACT9998 VAL1000 manifest only. P1 and CAD-Recode are summarized from frozen V2 per-case artifacts. DeepCAD, CADFit, and Cadrille are not assigned fabricated values.

`IR` is explicitly defined in this closeout as usable frozen prediction artifact rate, separate from STEP Reload. IoU is computed by the same closeout evaluator as exact OCC solid intersection volume divided by fused union volume, after the frozen V2 coordinate adapter.

Denominators:

- P1: full 1000; STEP Reload 958; geometry-valid 239.
- CAD-Recode: full 1000; STEP Reload 840; geometry-valid 201.
- Strict P1/CAD-Recode common-valid: 190 exact IDs.
- IoU-valid after range validation: P1 238, CAD-Recode 198, strict common geometry-valid with IoU on both 187; out-of-range OCC boolean cases remain blank with case-level reasons.
- DeepCAD: no aligned prediction/STEP denominator.
- CADFit: 1000 normalized input cache files materialized, but no prediction/STEP outputs.
- Cadrille: no identified artifact.

Per-method-valid and strict common-valid metrics are kept separate. Means across different case sets are not used as strict cross-method winners. Exact IDs, paths, denominators, and failure reasons are in `tables/baseline_full_val1000.csv`.
''')

# Compact denominator-aware summaries; blanks are intentional for unavailable methods.
import csv
v=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/unified_step_geometry_evaluator_v2')
pm={r['case_id']:r for r in csv.DictReader((v/'per_case/P1_GEOMETRY_METRICS_V2.csv').open())}
cm={r['case_id']:r for r in csv.DictReader((v/'per_case/CAD_RECODE_GEOMETRY_METRICS_V2.csv').open())}
common=[c for c in pm if pm[c].get('geometry_eval_success')=='True' and cm.get(c,{}).get('geometry_eval_success')=='True']
def stats(d,k):
    a=sorted(float(x[k]) for x in d if x.get('geometry_eval_success')=='True')
    if not a:return ('','','','')
    return (len(a),sum(a)/len(a),a[len(a)//2],a[-1])
with (O/'tables'/'baseline_per_method_valid_summary.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['method','full_denominator','step_reload_n','geometry_valid_n','metric','mean','median','max','strict_common_valid_n'])
    for name,d in [('P1',list(pm.values())),('CAD-Recode',list(cm.values()))]:
        for k in ['chamfer','h95','relative_volume_error']:
            n,mean,median,mx=stats(d,k); w.writerow([name,1000,sum(x.get('step_reload_success')=='True' for x in d),n,k,mean,median,mx,len(common)])
    for name in ['DeepCAD','CADFit','Cadrille']:
        w.writerow([name,1000,'',0,'','','','',0])
