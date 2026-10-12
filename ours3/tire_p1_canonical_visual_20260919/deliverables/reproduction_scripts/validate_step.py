from pathlib import Path
import cadquery as cq
import json
root=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/tire_p1_canonical_visual_20260919/deliverables')
s=cq.importers.importStep(str(root/'tire_p1.step')).val()
data={'step_reimport_success':True,'valid':s.isValid(),'solid_count':len(s.Solids()),'face_count':len(s.Faces()),'edge_count':len(s.Edges()),'volume':s.Volume()}
(root/'step_validation.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data))
