import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-33))
r=w0.sketch().segment((-100,-45),(-74,-45)).segment((-74,-50)).segment((93,-50)).segment((93,-45)).segment((100,-45)).segment((100,50)).segment((-100,50)).close().assemble().push([(-66,20)]).circle(27,mode='s').push([(29,0)]).circle(22,mode='s').finalize().extrude(66).union(w0.sketch().segment((-93,-50),(100,-50)).segment((100,50)).segment((-38,50)).arc((-51,28),(-74,17)).segment((-74,-28)).segment((-93,-28)).close().assemble().push([(13,0)]).circle(4,mode='s').finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0059_00592217.step')
