import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-36))
r=w0.sketch().segment((-100,-36),(-65,-36)).segment((-65,-34)).segment((-62,-34)).segment((-62,-36)).segment((93,-36)).segment((93,-32)).segment((100,-32)).segment((100,36)).segment((71,36)).arc((69,33),(67,36)).segment((-46,36)).segment((-46,37)).segment((-100,37)).close().assemble().reset().face(w0.sketch().segment((-62,-29),(-62,-27)).arc((-63,-28),(-62,-29)).assemble(),mode='s').reset().face(w0.sketch().arc((-61,-30),(-59,-31),(-57,-30)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-46,-29),(-45,-28),(-46,-27)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-46,37),(-45,33),(-46,30)).close().assemble(),mode='s').finalize().extrude(72)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0088_00883438.step')
