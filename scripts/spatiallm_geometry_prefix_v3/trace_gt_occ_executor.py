#!/usr/bin/env python3
"""One-sample, no-model trace of the V3 CAD executor's actual OCC object."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_decode_dev_50.json'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'


def module():
    spec = importlib.util.spec_from_file_location('trace_cad_dsl', EXECUTOR)
    m = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def summary_obj(x):
    out = {'python_type': f'{type(x).__module__}.{type(x).__name__}', 'repr': repr(x)[:1200], 'attrs': sorted(a for a in ('val','wrapped','ShapeType','IsNull','IsValid','Solids','Faces','Volume') if hasattr(x, a))}
    for key in ('IsNull', 'IsValid', 'ShapeType'):
        if hasattr(x, key):
            try: out[key] = str(getattr(x, key)())
            except Exception as e: out[key + '_error'] = repr(e)
    for key in ('Solids', 'Faces'):
        if hasattr(x, key):
            try: out[key + '_count'] = len(getattr(x, key)())
            except Exception as e: out[key + '_error'] = repr(e)
    return out


def main():
    rows = json.loads(DATA.read_text())['records']
    # First minimal Box target in frozen dev, falling back to first row.
    row = next((r for r in rows if 'Box(' in pathlib.Path(r['target_dsl']).read_text() and pathlib.Path(r['target_dsl']).read_text().count('body_') <= 3), rows[0])
    text = pathlib.Path(row['target_dsl']).read_text(); m = module(); code = m.extract_dsl_code(text); program = m.parse_dsl(code)
    shapes = {}
    for name, node in program.assignments.items():
        if name != 'result': shapes[name] = m._build_shape(node, shapes) if isinstance(node, dict) and 'op' in node else node
    node = program.assignments['result']; result = shapes[node] if isinstance(node, str) else m._build_shape(node, shapes)
    val = result.val() if hasattr(result, 'val') else result
    wrapped = val.wrapped if hasattr(val, 'wrapped') else val
    out = {'cad_id': row['cad_id'], 'dsl_executor_module': str(EXECUTOR), 'dsl_executor_sha256': hashlib.sha256(EXECUTOR.read_bytes()).hexdigest(), 'gt_dsl': text, 'parser_return': summary_obj(program), 'executor_result': summary_obj(result), 'result_val': summary_obj(val), 'occ_candidate': summary_obj(wrapped)}
    try:
        from OCP.BRepCheck import BRepCheck_Analyzer
        out['brep_analyzer_valid'] = bool(BRepCheck_Analyzer(wrapped).IsValid())
    except Exception as e: out['brep_analyzer_error'] = repr(e)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / 'gt.step'
        try:
            from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
            from OCP.IFSelect import IFSelect_RetDone
            writer = STEPControl_Writer(); transfer = writer.Transfer(wrapped, STEPControl_AsIs); status = writer.Write(str(p))
            out['step_transfer_return'] = str(transfer); out['step_write_status'] = str(status); out['step_write_done'] = bool(status == IFSelect_RetDone); out['step_file_exists'] = p.exists(); out['step_file_bytes'] = p.stat().st_size if p.exists() else 0
        except Exception as e: out['step_write_error'] = repr(e)
        if p.exists():
            try:
                import cadquery as cq
                reloaded = cq.importers.importStep(str(p)); out['step_reload'] = True; out['reloaded_result'] = summary_obj(reloaded)
            except Exception as e: out['step_reload'] = False; out['step_reload_error'] = repr(e)
    target = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/cad_execution_failure_audit_v1/GT_OCC_SINGLE_TRACE.json'
    target.write_text(json.dumps(out, indent=2, default=str) + '\n')
    print(json.dumps(out, indent=2, default=str))


if __name__ == '__main__': main()
