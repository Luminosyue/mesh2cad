import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
r=w0.sketch().arc((-21,31),(-16,30),(-12,29)).segment((0,29)).segment((0,97)).segment((-3,97)).segment((-3,100)).segment((-21,100)).close().assemble().reset().face(w0.sketch().arc((-19,-70),(-18,-88),(-7,-99)).segment((-7,-88)).arc((-12,-80),(-9,-72)).arc((11,-74),(-7,-70)).arc((-12,-71),(-17,-69)).arc((18,-89),(-19,-70)).assemble()).finalize().extrude(56).union(w0.sketch().push([(-9,-75)]).circle(11).circle(4,mode='s').reset().face(w0.sketch().segment((-19,29),(-2,29)).segment((-2,46)).arc((0,52),(-2,58)).segment((-2,75)).segment((-19,75)).segment((-19,58)).arc((-21,52),(-19,46)).close().assemble()).finalize().extrude(56))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00537221.step')
