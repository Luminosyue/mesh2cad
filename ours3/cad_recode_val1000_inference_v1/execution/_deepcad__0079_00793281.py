import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().segment((-100,-12),(-93,-12)).segment((-93,-26)).segment((-68,-26)).segment((-68,-19)).segment((-52,-19)).segment((-52,-26)).segment((-47,-26)).segment((-47,-12)).segment((-29,-12)).segment((-29,-26)).segment((18,-26)).segment((18,-19)).segment((48,-19)).segment((48,-26)).segment((68,-26)).segment((68,-19)).segment((100,-19)).segment((100,22)).segment((68,22)).segment((68,26)).segment((33,26)).arc((28,18),(18,13)).segment((18,22)).segment((13,22)).segment((13,26)).segment((-16,26)).segment((-16,22)).segment((-29,22)).segment((-29,19)).segment((-52,19)).segment((-52,26)).segment((-93,26)).segment((-93,19)).segment((-100,19)).close().assemble().push([(61,6)]).circle(12,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00793281.step')
