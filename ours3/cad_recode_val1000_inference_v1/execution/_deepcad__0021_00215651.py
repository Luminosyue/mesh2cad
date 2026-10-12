import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
w1=cq.Workplane('XY',origin=(0,0,-60))
r=w0.sketch().segment((-100,-100),(95,-100)).segment((95,-86)).segment((100,-86)).segment((100,91)).segment((95,91)).segment((95,100)).segment((-95,100)).segment((-95,91)).segment((-100,91)).segment((-100,-86)).close().assemble().push([(-41,51)]).circle(19,mode='s').push([(17,-26)]).circle(31,mode='s').finalize().extrude(94).union(w1.sketch().arc((33,-97),(33,-72),(60,-72)).arc((-2,-24),(33,-97)).assemble().finalize().extrude(-40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0021_00215651.step')
