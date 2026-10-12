import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().segment((-8,-100),(1,-100)).segment((1,-86)).segment((8,-86)).segment((8,97)).segment((1,97)).segment((1,100)).segment((-8,100)).segment((-8,-15)).arc((-5,-20),(-8,-25)).close().assemble().push([(0,-47)]).circle(3,mode='s').finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00800887.step')
