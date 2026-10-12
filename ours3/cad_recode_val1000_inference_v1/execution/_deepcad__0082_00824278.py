import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-16))
r=w0.sketch().segment((-24,-100),(24,-100)).segment((24,100)).segment((-24,100)).segment((-24,-14)).segment((-20,-14)).segment((-20,-18)).segment((-24,-18)).close().assemble().push([(-18,-59)]).circle(2,mode='s').finalize().extrude(32)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00824278.step')
