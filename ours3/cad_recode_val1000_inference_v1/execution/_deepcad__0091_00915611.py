import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(45,0,0))
w1=cq.Workplane('YZ',origin=(-17,0,0))
r=w0.sketch().segment((-70,-97),(-18,-100)).segment((-18,-94)).segment((14,-94)).segment((14,-100)).segment((63,-100)).arc((-4,-5),(-70,-97)).assemble().finalize().extrude(-80).union(w0.sketch().segment((-31,67),(-25,67)).segment((-25,10)).segment((14,10)).segment((1,1)).arc((1,-54),(52,-37)).segment((25,-37)).segment((25,10)).segment((64,10)).segment((64,26)).segment((70,26)).segment((70,96)).segment((64,96)).segment((64,97)).segment((63,97)).segment((63,96)).segment((62,96)).segment((62,91)).segment((-25,91)).segment((-25,70)).segment((-31,70)).close().assemble().finalize().extrude(-5)).union(w1.sketch().segment((-31,-95),(64,-95)).segment((64,-37)).segment((70,-37)).segment((70,68)).segment((64,68)).segment((64,89)).segment((34,89)).segment((34,100)).segment((-26,100)).segment((-26,89)).segment((-31,89)).segment((-31,45)).arc((-30,44),(-31,43)).close().assemble().push([(17,-13)]).rect(94,142,mode='s').finalize().extrude(-5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0091_00915611.step')
