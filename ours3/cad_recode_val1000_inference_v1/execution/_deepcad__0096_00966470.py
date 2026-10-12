import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-100,-13),(-99,-13)).arc((-89,-40),(-62,-49)).segment((-44,-60)).segment((-35,-46)).arc((-25,-43),(-16,-37)).segment((-16,-56)).segment((-4,-56)).segment((-4,-46)).arc((29,-58),(61,-47)).segment((64,-47)).segment((64,-45)).arc((73,-41),(81,-35)).segment((81,-51)).segment((100,-51)).segment((100,15)).segment((91,15)).segment((91,22)).segment((43,60)).segment((34,46)).arc((24,52),(13,56)).segment((13,59)).segment((-16,59)).segment((-16,56)).arc((-34,49),(-50,38)).arc((-60,59),(-82,59)).segment((-92,59)).segment((-92,52)).arc((-97,47),(-100,41)).close().assemble().push([(-55,13)]).circle(27,mode='s').push([(16,24)]).circle(21,mode='s').push([(56,-14)]).circle(2,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0096_00966470.step')
