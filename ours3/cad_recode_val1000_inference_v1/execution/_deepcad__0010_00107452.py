import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-71))
w1=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().arc((-39,0),(-34,-7),(-28,-14)).segment((-28,-18)).segment((-24,-18)).arc((-5,-34),(20,-31)).segment((15,-31)).segment((15,-21)).arc((-16,14),(20,-14)).segment((28,-14)).segment((28,-19)).arc((34,-7),(37,5)).segment((21,-3)).arc((-10,-28),(-29,4)).close().assemble().reset().face(w0.sketch().segment((-28,19),(-20,21)).arc((10,38),(29,1)).segment((37,-4)).arc((34,7),(28,14)).segment((28,18)).segment((24,18)).arc((5,34),(-20,19)).close().assemble()).finalize().extrude(-29).union(w0.sketch().segment((-39,0),(-20,0)).arc((0,-22),(20,0)).segment((39,0)).segment((39,4)).segment((20,4)).arc((0,26),(-20,4)).segment((-39,4)).close().assemble().finalize().extrude(163)).union(w1.sketch().arc((-100,-19),(-76,-10),(-53,-10)).arc((12,10),(70,-24)).arc((85,-20),(100,-23)).segment((100,28)).arc((21,16),(-40,27)).arc((-42,14),(-49,4)).arc((-50,9),(-51,14)).arc((-77,-3),(-100,-19)).assemble().finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00107452.step')
