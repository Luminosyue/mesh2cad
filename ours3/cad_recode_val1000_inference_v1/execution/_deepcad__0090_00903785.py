import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-14,0))
r=w0.sketch().segment((-100,-25),(98,-25)).segment((98,-21)).segment((100,-21)).segment((100,25)).segment((-100,25)).close().assemble().push([(-61,5)]).circle(19,mode='s').reset().face(w0.sketch().segment((28,-25),(38,-25)).segment((38,-21)).segment((35,-21)).segment((35,-18)).segment((38,-18)).segment((38,-14)).segment((28,-14)).close().assemble(),mode='s').reset().face(w0.sketch().segment((45,21),(48,21)).segment((48,25)).segment((45,25)).arc((66,1),(45,21)).assemble(),mode='s').finalize().extrude(28)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0090_00903785.step')
