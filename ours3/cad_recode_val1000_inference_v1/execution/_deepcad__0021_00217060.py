import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-85))
r=w0.sketch().segment((-99,-40),(-98,-40)).segment((-98,-46)).segment((-81,-46)).arc((-53,-61),(-24,-46)).segment((98,-46)).segment((98,40)).segment((98,46)).segment((98,61)).segment((24,61)).arc((0,66),(-24,61)).segment((-98,61)).segment((-98,40)).segment((-99,40)).close().assemble().finalize().extrude(-15).union(w0.sketch().segment((-83,-46),(98,-46)).segment((98,62)).segment((50,62)).arc((35,24),(32,64)).segment((32,62)).segment((-83,62)).close().assemble().push([(-53,-44)]).circle(2,mode='s').push([(-51,-48)]).circle(2,mode='s').finalize().extrude(185)).union(w0.workplane(offset=185/2).moveTo(16,6).box(146,112,185))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0021_00217060.step')
