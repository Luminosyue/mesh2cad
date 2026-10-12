from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
import sys

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/dsl_v2_placement_lowering_audit_v1'
sys.path.insert(0, str(ROOT / 'scripts'))
import canonical_cad_dsl_v2 as v2

CASES = {
    'CENTER_TO_ORIGIN': {
        'source': 'import cadquery as cq\nresult = cq.Workplane("XY").center(3.0, 4.0).rect(10.0, 6.0).extrude(2.0)\n',
        'dsl': 'result = Box(width=10.0, depth=6.0, height=2.0, origin=[3.0, 4.0, 0.0], x_axis=[1.0, 0.0, 0.0])\n',
    },
    'TRANSLATE_TO_ORIGIN': {
        'source': 'import cadquery as cq\nresult = cq.Workplane("XY").box(4.0, 5.0, 6.0, centered=(False, False, False)).translate((7.0, 8.0, 9.0))\n',
        'dsl': 'result = Box(width=4.0, depth=5.0, height=6.0, origin=[9.0, 10.5, 9.0], x_axis=[1.0, 0.0, 0.0])\n',
    },
    'WORKPLANE_OFFSET_TO_ORIGIN': {
        'source': 'import cadquery as cq\nresult = cq.Workplane("XY").workplane(offset=3.0).rect(8.0, 2.0).extrude(4.0)\n',
        'dsl': 'result = Box(width=8.0, depth=2.0, height=4.0, origin=[0.0, 0.0, 3.0], x_axis=[1.0, 0.0, 0.0])\n',
    },
}

def info(path):
    import cadquery as cq
    shape = cq.importers.importStep(str(path)).val(); bb = shape.BoundingBox()
    return {'bbox': [float(x) for x in (bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax)], 'volume': float(shape.Volume()), 'area': float(shape.Area()), 'faces': len(shape.Faces()), 'solids': len(shape.Solids())}

def main():
    rows = []
    for name, case in CASES.items():
        rec = {'case': name, 'rule': name, 'source_exec': False, 'dsl_exec': False, 'pass': False}
        with tempfile.TemporaryDirectory(prefix='placement_lowering_') as td:
            sp = Path(td) / 'source.py'; ss = Path(td) / 'source.step'; ds = Path(td) / 'dsl.step'; sp.write_text(case['source'])
            runner = case['source'] + '\nimport cadquery as _cq_audit\n_cq_audit.exporters.export(result, ' + repr(str(ss)) + ', exportType="STEP")\n'
            rp = Path(td) / 'run.py'; rp.write_text(runner); proc = subprocess.run(['python3', str(rp)], capture_output=True, text=True, timeout=120)
            rec['source_exec'] = proc.returncode == 0 and ss.exists()
            try:
                v2.execute(case['dsl'], ds); rec['dsl_exec'] = ds.exists()
                si, di = info(ss), info(ds); rec['source'] = si; rec['dsl'] = di
                scale = max(1.0, max(abs(x) for x in si['bbox'] + di['bbox']))
                rec['bbox_relative_error'] = max(abs(a-b) for a,b in zip(si['bbox'], di['bbox'])) / scale
                rec['volume_relative_error'] = abs(si['volume']-di['volume']) / max(1.0, abs(si['volume']))
                rec['surface_area_relative_error'] = abs(si['area']-di['area']) / max(1.0, abs(si['area']))
                rec['pass'] = rec['source_exec'] and rec['dsl_exec'] and rec['bbox_relative_error'] < 1e-6 and rec['volume_relative_error'] < 1e-6 and rec['surface_area_relative_error'] < 1e-6 and si['faces'] == di['faces'] and si['solids'] == di['solids']
            except Exception as exc: rec['error'] = repr(exc)
            if proc.returncode != 0: rec['source_error'] = proc.stderr[-2000:]
        rows.append(rec)
    (OUT/'PLACEMENT_LOWERING_SEMANTIC_CANARY.json').write_text(json.dumps({'cases': rows, 'pass': sum(x['pass'] for x in rows), 'count': len(rows), 'new_dsl_operator_added': False}, indent=2) + '\n')
    print(json.dumps({'pass': sum(x['pass'] for x in rows), 'count': len(rows), 'cases': rows}, indent=2))

if __name__ == '__main__': main()
