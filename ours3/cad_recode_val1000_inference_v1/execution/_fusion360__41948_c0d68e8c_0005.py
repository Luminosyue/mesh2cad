import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-9))
r=w0.sketch().segment((-100,10),(-99,11)).arc((-84,-54),(-35,-94)).segment((-40,-75)).arc((-74,-43),(-86,4)).close().assemble().reset().face(w0.sketch().segment((-64,77),(60,65)).segment((60,61)).arc((76,40),(85,13)).segment((86,13)).segment((86,-13)).segment((85,-13)).arc((81,-27),(74,-41)).segment((80,-60)).arc((100,0),(73,59)).segment((81,59)).arc((1,100),(-64,77)).assemble()).reset().face(w0.sketch().arc((-31,-95),(1,-100),(32,-95)).close().assemble()).finalize().extrude(18)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__41948_c0d68e8c_0005.step')
