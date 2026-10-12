import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
r=w0.sketch().segment((-77,-100),(77,-100)).segment((77,-18)).segment((-77,-53)).close().assemble().reset().face(w0.sketch().segment((-77,-53),(77,18)).segment((77,100)).segment((-77,100)).close().assemble()).finalize().extrude(58)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0077_00779359.step')
