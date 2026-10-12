import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,13,0))
w1=cq.Workplane('ZX',origin=(0,34,0))
r=w0.sketch().arc((-12,-4),(12,3),(-12,0)).arc((-10,-1),(-12,-4)).assemble().push([(1,0)]).circle(10,mode='s').finalize().extrude(-113).union(w0.sketch().arc((-8,-9),(12,0),(-8,9)).arc((-13,0),(-8,-9)).assemble().finalize().extrude(82)).union(w0.sketch().arc((-9,-8),(-8,-7),(-8,-6)).segment((-9,-6)).close().assemble().finalize().extrude(87)).union(w1.workplane(offset=-112/2).moveTo(0,1).cylinder(112,10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00335037.step')
