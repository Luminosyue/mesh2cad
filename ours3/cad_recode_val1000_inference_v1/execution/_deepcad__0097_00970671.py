import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-100,-5),(-91,-5)).segment((-91,-9)).segment((91,-9)).segment((91,-5)).segment((97,-5)).segment((97,5)).segment((91,5)).segment((91,9)).segment((68,9)).arc((67,5),(65,9)).segment((9,9)).segment((9,5)).segment((-91,5)).segment((-91,9)).segment((-100,9)).close().assemble().reset().face(w0.sketch().segment((-47,-5),(-45,-5)).segment((-45,-4)).segment((-47,-3)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-47,4),(-45,3)).segment((-45,5)).segment((-47,5)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-39,-9),(39,-9)).segment((39,9)).segment((10,9)).segment((10,-9)).close().assemble(),mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00970671.step')
