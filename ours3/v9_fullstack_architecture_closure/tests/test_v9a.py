import json
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/v9_fullstack_architecture_closure')
def summary():return json.loads((ROOT/'artifacts/v9a_summary.json').read_text())
def test_all_eight_real_fitters():assert summary()['REAL_SURFACE_FITTER_COUNT']==8 and all(summary()['REAL_FITTERS'].values())
def test_no_string_only():assert summary()['PRIMITIVE_STRING_ONLY_COUNT']==0
def test_real_parameter_dependencies():assert summary()['PRIMITIVE_PARAMETER_PERTURBATION_EFFECTIVE'] and all(summary()['DEPENDENCY_TESTS'].values())
def test_real_parameters_present():
 s=summary()['records'];assert s['CYLINDER']['parameters']['radius']>0;assert s['REVOLUTION']['parameters']['generatrix_points'];assert s['EXTRUSION']['parameters']['depth']>0;assert s['SWEEP']['parameters']['spine_curve'];assert s['LOFT']['parameters']['measured_profile_references'];assert s['PERIODIC_BSPLINE']['parameters']['periodic_v'];assert s['GENERAL_BSPLINE']['parameters']['control_points']
def test_support_and_errors_present():
 for r in summary()['records'].values():assert r['support_points'] and 'fit_residual' in r and 'normal_consistency_error' in r and 'boundary_consistency_error' in r and r['surface_domain']
