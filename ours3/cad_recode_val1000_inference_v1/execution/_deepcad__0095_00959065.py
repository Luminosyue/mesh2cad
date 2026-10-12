import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-86,0))
r=w0.sketch().arc((-28,11),(-29,-7),(-22,-20)).close().assemble().reset().face(w0.sketch().segment((-25,16),(-19,23)).arc((-22,19),(-25,16)).assemble()).reset().face(w0.sketch().arc((-19,-23),(-16,-24),(-13,-25)).close().assemble()).reset().face(w0.sketch().segment((-11,29),(20,22)).arc((5,29),(-11,29)).assemble()).reset().face(w0.sketch().arc((13,-14),(16,-10),(19,-7)).close().assemble()).reset().face(w0.sketch().arc((22,-20),(25,-16),(28,-11)).close().assemble()).reset().face(w0.sketch().segment((25,16),(29,6)).arc((29,10),(25,16)).assemble()).finalize().extrude(167).union(w0.sketch().segment((-30,-3),(23,19)).arc((-12,28),(-30,-3)).assemble().reset().face(w0.sketch().arc((-23,-19),(12,-28),(30,3)).close().assemble()).finalize().extrude(200)).union(w1.workplane(offset=153/2).moveTo(0,-1).cylinder(153,18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0095_00959065.step')
