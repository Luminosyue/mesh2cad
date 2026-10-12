import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-5,0))
r=w0.sketch().segment((-100,14),(-89,1)).segment((-96,-29)).segment((-72,-35)).segment((-59,-56)).segment((-72,-34)).segment((-86,-29)).segment((-60,-75)).segment((-60,-76)).segment((-59,-76)).segment((-49,-91)).segment((-37,-84)).segment((-19,-99)).segment((-10,-88)).arc((-18,-58),(8,-40)).segment((14,-40)).segment((14,-73)).segment((17,-73)).segment((8,-99)).segment((71,-71)).segment((63,-52)).arc((71,-46),(78,-39)).segment((89,-45)).segment((96,-31)).segment((95,-31)).arc((99,15),(78,55)).segment((89,43)).segment((51,-7)).segment((51,19)).segment((88,48)).arc((70,55),(53,64)).arc((19,98),(-30,88)).segment((-31,89)).segment((-38,76)).arc((-77,61),(-100,19)).segment((-98,19)).close().assemble().reset().face(w0.sketch().segment((-80,10),(-21,-10)).segment((14,73)).segment((-45,93)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-16,-23),(14,-10)).segment((-16,-10)).close().assemble()).finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00738965.step')
