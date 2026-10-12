import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-14,-100),(-10,-100)).segment((-10,-61)).arc((-11,-60),(-10,-59)).segment((-10,-40)).arc((-11,-39),(-10,-38)).segment((-10,-14)).segment((-14,-14)).close().assemble().reset().face(w0.sketch().segment((-14,14),(-10,14)).segment((-10,38)).segment((-14,38)).segment((-14,32)).arc((-11,30),(-14,28)).close().assemble()).reset().face(w0.sketch().segment((10,-96),(14,-96)).segment((14,-40)).arc((11,-39),(14,-38)).segment((14,-14)).segment((10,-14)).segment((10,-59)).arc((11,-60),(10,-61)).close().assemble()).reset().face(w0.sketch().segment((10,32),(14,32)).segment((14,10)).arc((15,13),(15,16)).arc((13,17),(14,19)).arc((13,28),(10,36)).close().assemble()).reset().face(w0.sketch().segment((10,74),(14,74)).segment((14,83)).arc((12,82),(10,83)).close().assemble()).reset().face(w0.sketch().arc((-14,94),(-11,95),(-10,94)).segment((-10,100)).arc((-12,98),(-14,94)).assemble()).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00975692.step')
