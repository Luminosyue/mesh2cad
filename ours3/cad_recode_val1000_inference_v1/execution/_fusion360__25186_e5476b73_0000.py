import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-63,0,0))
w1=cq.Workplane('YZ',origin=(-94,0,0))
r=w0.sketch().segment((-25,-3),(-20,-3)).arc((-21,1),(-20,7)).segment((-25,7)).close().assemble().reset().face(w0.sketch().segment((-22,-12),(-17,-18)).segment((-17,-12)).close().assemble()).reset().face(w0.sketch().segment((-15,-19),(-5,-25)).segment((-1,-20)).arc((-8,-19),(-15,-19)).assemble()).finalize().extrude(-37).union(w0.sketch().push([(2,2)]).circle(23).circle(19,mode='s').finalize().extrude(159)).union(w1.sketch().arc((-21,0),(10,22),(20,-14)).segment((20,5)).segment((15,5)).arc((10,15),(3,5)).segment((-16,5)).arc((-18,2),(-21,0)).assemble().finalize().extrude(67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__25186_e5476b73_0000.step')
