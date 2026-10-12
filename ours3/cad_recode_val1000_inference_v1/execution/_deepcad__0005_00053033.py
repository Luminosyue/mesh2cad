import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-31))
r=w0.sketch().segment((-92,-100),(92,-100)).segment((92,100)).segment((-92,100)).segment((-92,54)).arc((-89,53),(-92,52)).close().assemble().push([(13,-29)]).circle(41,mode='s').finalize().extrude(42).union(w0.sketch().segment((-92,-39),(-77,-39)).arc((-39,-47),(-1,-39)).segment((14,-39)).segment((14,-27)).arc((30,2),(14,31)).segment((14,53)).segment((-1,53)).arc((-39,62),(-77,53)).segment((-92,53)).close().assemble().finalize().extrude(62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00053033.step')
