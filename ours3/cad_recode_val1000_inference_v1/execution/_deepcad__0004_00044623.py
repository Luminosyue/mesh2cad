import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,67,0))
w1=cq.Workplane('YZ',origin=(-33,0,0))
r=w0.sketch().segment((-50,-100),(50,-100)).segment((50,-33)).segment((20,-33)).segment((20,-34)).segment((-49,-4)).segment((-28,18)).segment((-50,18)).segment((-50,-42)).arc((-51,-46),(-50,-50)).close().assemble().reset().face(w0.sketch().segment((-50,42),(-45,42)).segment((-50,49)).close().assemble()).reset().face(w0.sketch().segment((-50,50),(-44,78)).segment((-50,78)).close().assemble()).reset().face(w0.sketch().segment((-50,79),(-44,78)).segment((-49,100)).segment((-50,100)).close().assemble()).reset().face(w0.sketch().segment((-41,42),(-34,42)).segment((-34,43)).close().assemble()).reset().face(w0.sketch().segment((-41,78),(-34,78)).segment((-34,79)).close().assemble()).finalize().extrude(-134).union(w1.sketch().arc((-16,36),(18,24),(50,4)).segment((50,50)).segment((-16,50)).close().assemble().finalize().extrude(-67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0004_00044623.step')
