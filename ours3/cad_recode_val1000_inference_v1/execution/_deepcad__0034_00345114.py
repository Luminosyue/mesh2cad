import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-40))
w1=cq.Workplane('YZ',origin=(-60,0,0))
r=w0.sketch().segment((-100,-23),(-82,-23)).segment((-100,19)).close().assemble().reset().face(w0.sketch().segment((-84,52),(75,20)).segment((57,20)).segment((57,18)).segment((55,18)).segment((55,20)).segment((-84,54)).close().assemble()).reset().face(w0.sketch().segment((-30,-6),(35,11)).segment((35,18)).segment((55,18)).segment((55,20)).segment((57,20)).segment((57,18)).segment((60,18)).segment((60,20)).segment((75,20)).close().assemble()).finalize().extrude(4).union(w0.sketch().segment((-100,-60),(-60,-60)).segment((-60,-19)).segment((-17,-6)).arc((-34,-12),(-49,-17)).segment((-49,-18)).segment((-51,-18)).arc((-55,-19),(-60,-19)).segment((-60,60)).segment((-100,60)).close().assemble().reset().face(w0.sketch().arc((-21,55),(-10,51),(-1,45)).segment((3,60)).segment((-21,60)).close().assemble()).reset().face(w0.sketch().arc((23,37),(30,26),(37,12)).arc((39,14),(40,17)).segment((40,20)).segment((100,20)).segment((100,60)).segment((40,60)).segment((40,61)).close().assemble()).finalize().extrude(80)).union(w1.workplane(offset=-40/2).moveTo(-56.5,0).box(7,50,40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0034_00345114.step')
