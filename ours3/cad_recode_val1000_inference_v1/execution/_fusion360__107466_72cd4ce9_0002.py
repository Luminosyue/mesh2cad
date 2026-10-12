import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-81,-20),(-40,-20)).segment((-77,-10)).segment((-69,17)).segment((-81,17)).segment((-81,9)).arc((-100,-2),(-81,-14)).close().assemble().reset().face(w0.sketch().segment((-75,-20),(-41,-20)).segment((-41,-14)).arc((-39,-19),(-37,-20)).segment((-15,-20)).segment((-15,-19)).segment((-17,-19)).segment((-17,-17)).segment((-15,-17)).segment((-15,-14)).arc((-17,-16),(-19,-19)).segment((-19,-20)).segment((70,-20)).segment((70,-19)).segment((86,-19)).segment((86,-7)).segment((70,-7)).segment((70,20)).segment((-75,20)).close().assemble()).finalize().extrude(20).union(w1.sketch().push([(2,4)]).circle(11).circle(3,mode='s').finalize().extrude(-11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__107466_72cd4ce9_0002.step')
