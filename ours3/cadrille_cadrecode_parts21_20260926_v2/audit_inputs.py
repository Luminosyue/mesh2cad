import json
from pathlib import Path
import numpy as np
import trimesh
root=Path(__file__).resolve().parent
m=json.loads((root/'MANIFEST.json').read_text());rows=[]
for case in m['cases']:
    bounds=np.array([trimesh.load(x['input_stl'],force='mesh',process=False).bounds for x in case['parts']])
    part_bounds=np.array([bounds[:,0].min(0),bounds[:,1].max(0)])
    full=trimesh.load(case['full_mesh'],force='mesh',process=False)
    size=max(full.extents)
    row=dict(case=case['case'],source_mesh_bounds=full.bounds.tolist(),assembled_part_bounds=part_bounds.tolist(),max_bound_discrepancy_over_source_extent=float(np.abs(part_bounds-full.bounds).max()/size),source_extent=float(size),parts_extent=float((part_bounds[1]-part_bounds[0]).max()))
    rows.append(row);print(case['case'],round(row['max_bound_discrepancy_over_source_extent'],4),flush=True)
(root/'INPUT_COORDINATE_AUDIT.json').write_text(json.dumps(rows,indent=2))
