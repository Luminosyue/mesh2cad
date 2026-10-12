import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-27,0,0))
r=w0.sketch().segment((-41,-14),(-36,-14)).segment((-36,-100)).segment((65,-100)).segment((65,100)).segment((-65,100)).segment((-65,65)).segment((-20,65)).segment((-20,68)).segment((-17,68)).segment((-17,65)).segment((15,65)).segment((15,32)).segment((-17,32)).segment((-17,29)).segment((-20,29)).segment((-20,32)).segment((-41,32)).close().assemble().reset().face(w0.sketch().segment((-65,-65),(-65,-16)).arc((-66,-40),(-65,-65)).assemble()).finalize().extrude(54).union(w0.sketch().segment((-65,-96),(65,-96)).segment((65,96)).segment((-65,96)).segment((-65,14)).arc((-40,-14),(-65,-42)).close().assemble().circle(30,mode='s').finalize().extrude(54))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00198536.step')
