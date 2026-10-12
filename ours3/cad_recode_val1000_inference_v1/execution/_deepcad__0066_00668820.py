import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-33))
w1=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-96,29),(-49,-12)).segment((-49,35)).segment((-64,43)).arc((-80,28),(-96,29)).assemble().finalize().extrude(4).union(w0.sketch().segment((-100,-46),(-93,-46)).segment((-93,-50)).segment((-67,-50)).segment((-67,-10)).segment((-100,14)).close().assemble().reset().face(w0.sketch().segment((-100,33),(-93,46)).segment((-93,50)).segment((-100,50)).close().assemble()).reset().face(w0.sketch().segment((-80,50),(-11,10)).segment((100,10)).segment((100,50)).close().assemble()).reset().face(w0.sketch().segment((22,30),(28,28)).segment((30,35)).segment((24,37)).close().assemble(),mode='s').finalize().extrude(66)).union(w1.sketch().arc((-62,-15),(-23,1),(-1,38)).segment((-62,38)).close().assemble().finalize().extrude(-26))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0066_00668820.step')
