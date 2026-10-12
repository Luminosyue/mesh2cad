import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
r=w0.sketch().segment((-93,36),(-90,32)).arc((-89,-40),(-33,-89)).segment((-33,-95)).segment((-21,-96)).segment((-21,-95)).segment((-19,-95)).segment((-19,-96)).segment((-18,-96)).segment((-18,-93)).arc((40,-91),(84,-52)).segment((93,-46)).segment((90,-42)).arc((89,43),(33,94)).segment((33,95)).segment((31,95)).arc((-40,92),(-84,39)).close().assemble().circle(74,mode='s').finalize().extrude(38).union(w0.sketch().arc((-99,-5),(-88,-44),(-65,-75)).segment((-65,-70)).close().assemble().reset().face(w0.sketch().segment((-72,47),(-51,52)).arc((-19,74),(19,70)).segment((30,70)).segment((30,63)).arc((35,61),(41,60)).segment((62,65)).arc((-10,98),(-72,47)).assemble()).reset().face(w0.sketch().arc((-46,-88),(1,-99),(47,-84)).segment((26,-84)).segment((26,-70)).arc((1,-74),(-24,-70)).close().assemble()).reset().face(w0.sketch().arc((53,-83),(94,-31),(90,36)).segment((69,31)).arc((73,-10),(53,-51)).close().assemble()).finalize().extrude(58))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0043_00439848.step')
