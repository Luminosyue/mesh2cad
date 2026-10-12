import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-26))
w1=cq.Workplane('XY',origin=(0,0,-23))
r=w0.sketch().segment((-96,19),(-43,-58)).segment((33,-3)).segment((-10,55)).arc((-44,58),(-75,45)).segment((-78,45)).segment((-78,43)).arc((-80,39),(-81,35)).close().assemble().push([(-43,12)]).circle(30,mode='s').reset().face(w0.sketch().segment((42,-33),(65,-40)).segment((77,-10)).arc((59,-19),(42,-33)).assemble()).reset().face(w0.sketch().arc((42,33),(60,27),(74,13)).segment((77,20)).segment((99,4)).segment((100,8)).segment((84,15)).segment((90,27)).segment((67,38)).segment((55,18)).arc((49,21),(42,23)).close().assemble()).finalize().extrude(33).union(w0.sketch().arc((-54,-56),(-34,-56),(-15,-49)).segment((-11,-49)).segment((-11,-48)).arc((1,-38),(10,-25)).segment((37,-25)).segment((37,-14)).segment((14,-14)).arc((15,10),(4,30)).segment((4,19)).segment((-1,19)).arc((-10,1),(-10,-19)).arc((-20,-28),(-28,-39)).arc((-37,-51),(-54,-56)).assemble().finalize().extrude(52)).union(w1.workplane(offset=47/2).moveTo(56,-17).cylinder(47,3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00826556.step')
