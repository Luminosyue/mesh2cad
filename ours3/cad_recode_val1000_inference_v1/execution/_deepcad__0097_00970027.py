import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-100,-35),(-52,-35)).arc((-56,-29),(-57,-22)).segment((-77,-22)).segment((-77,-13)).segment((-57,-13)).arc((-56,-6),(-52,0)).segment((-100,0)).close().assemble().reset().face(w0.sketch().segment((-49,12),(-29,12)).segment((-29,-13)).segment((-9,-13)).segment((-9,-22)).segment((-29,-22)).arc((-30,-28),(-35,-35)).segment((-15,-35)).segment((-15,-34)).segment((16,-35)).segment((16,-13)).segment((48,-13)).segment((48,-35)).segment((100,-35)).segment((100,35)).segment((23,35)).segment((23,32)).segment((-19,35)).segment((-19,31)).segment((-34,31)).segment((-34,35)).segment((-49,35)).close().assemble()).push([(3,16)]).circle(7,mode='s').push([(61,13)]).circle(14,mode='s').finalize().extrude(-9)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00970027.step')
