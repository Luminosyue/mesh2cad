import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-50,0))
w1=cq.Workplane('XY',origin=(0,0,3))
r=w0.sketch().segment((-15,75),(33,75)).segment((33,50)).segment((47,50)).segment((47,18)).segment((63,18)).segment((63,28)).arc((52,54),(59,81)).segment((47,81)).segment((47,77)).segment((33,77)).segment((33,76)).segment((-15,76)).close().assemble().push([(61,64)]).circle(2,mode='s').finalize().extrude(38).union(w0.sketch().segment((-84,22),(-41,22)).segment((-41,-50)).segment((-3,-88)).segment((13,-72)).arc((-11,-44),(10,-15)).segment((10,-30)).segment((85,-30)).arc((74,-4),(57,18)).segment((59,27)).segment((47,30)).segment((47,50)).segment((3,50)).segment((3,88)).segment((-84,88)).close().assemble().reset().face(w0.sketch().segment((6,-100),(84,-100)).segment((84,-50)).segment((82,-50)).arc((55,-94),(6,-96)).close().assemble()).push([(61,75.5)]).rect(46,49).finalize().extrude(100)).union(w1.workplane(offset=-88/2).moveTo(44,-19).box(62,12,88))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00308463.step')
