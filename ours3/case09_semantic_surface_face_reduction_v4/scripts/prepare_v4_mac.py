#!/usr/bin/env python3
import json,shutil
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'case09_semantic_surface_face_reduction_v4'
diag=json.loads((OUT/'metrics/wing_topology_diagnosis.json').read_text())
probe=json.loads((OUT/'metrics/semantic_surface_probe.json').read_text())
for part in ('CADPART_001','CADPART_002'):
    run=OUT/'04_mac'/part;run.mkdir(parents=True,exist_ok=True)
    old=json.loads(Path(diag['wings'][part]['selected_v3_spec']).read_text())
    selected=probe[part]['selected']
    spec={'schema':'SEMANTIC_WING_SPEC_V4','part_id':part,'representation':selected['representation'],
          'measured_v3_spec':old,'probe_qa':selected,
          'constraints':{'sections_are_fitting_constraints_only':True,'upper_skin_faces':1,
          'lower_skin_faces':1,'max_faces':6,'minimum_geometry_q':'Q2'}}
    (run/'measured_cad_spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    for name in ('cad_feature_graph.json','semantic_surface_graph.json'):
        shutil.copy2(OUT/'03_semantic_surface'/part/name,run/name)
print('V4_MAC_INPUTS_READY')
