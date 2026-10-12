import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-100,10),(-92,-14)).segment((-68,-12)).segment((-68,13)).close().assemble().reset().face(w0.sketch().segment((-57,-14),(-30,-12)).segment((-30,-14)).segment((15,-14)).segment((15,-11)).segment((47,-11)).arc((63,-14),(78,-11)).segment((100,-11)).segment((100,14)).segment((78,14)).arc((63,16),(47,14)).segment((33,14)).segment((33,11)).segment((15,11)).segment((15,14)).segment((-30,14)).segment((-30,12)).segment((-57,12)).close().assemble()).finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00169455.step')
