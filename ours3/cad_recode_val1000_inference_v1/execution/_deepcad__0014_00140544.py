import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-31,0))
r=w0.sketch().segment((-19,-100),(15,-100)).segment((15,-84)).segment((19,-84)).segment((19,98)).segment((10,98)).segment((10,100)).segment((-14,100)).segment((-14,98)).segment((-19,98)).segment((-19,-84)).close().assemble().reset().face(w0.sketch().segment((-19,-74),(-19,-26)).arc((-24,-50),(-19,-74)).assemble(),mode='s').reset().face(w0.sketch().arc((10,-74),(15,-50),(10,-26)).close().assemble(),mode='s').finalize().extrude(62).union(w0.workplane(offset=62/2).moveTo(-1,0).box(36,182,62))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00140544.step')
