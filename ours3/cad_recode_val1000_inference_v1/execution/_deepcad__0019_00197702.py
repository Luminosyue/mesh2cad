import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,53,0))
r=w0.sketch().arc((-35,-92),(-33,-96),(-31,-100)).segment((26,-100)).arc((30,-35),(35,29)).segment((35,100)).segment((-35,100)).segment((-35,68)).arc((-33,64),(-35,60)).segment((-35,5)).arc((-33,0),(-35,-5)).close().assemble().reset().face(w0.sketch().segment((-35,-5),(-35,5)).arc((-36,0),(-35,-5)).assemble(),mode='s').reset().face(w0.sketch().arc((-31,-100),(0,-99),(31,-100)).segment((-26,-100)).close().assemble()).finalize().extrude(-106).union(w0.workplane(offset=-37/2).moveTo(-10,0).box(48,154,37))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00197702.step')
