import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,27))
w1=cq.Workplane('YZ',origin=(-21,0,0))
r=w0.sketch().segment((-25,-97),(-15,-97)).segment((-15,-30)).arc((-19,-31),(-25,-30)).close().assemble().finalize().extrude(-5).union(w0.sketch().segment((-25,-97),(25,-97)).segment((25,-78)).arc((27,-64),(25,-51)).segment((25,-32)).segment((27,-32)).segment((27,-11)).segment((25,-11)).segment((25,-7)).segment((23,-7)).segment((27,35)).arc((21,31),(15,27)).segment((15,12)).segment((4,12)).segment((4,27)).arc((-12,42),(-19,61)).segment((-25,61)).segment((-25,42)).arc((-14,16),(-25,-9)).segment((-25,-28)).arc((-27,-31),(-25,-32)).segment((-25,-51)).arc((-27,-64),(-25,-78)).close().assemble().reset().face(w0.sketch().segment((-25,61),(4,61)).segment((4,60)).arc((15,58),(25,53)).segment((25,61)).segment((27,61)).segment((27,74)).segment((25,74)).segment((25,100)).segment((-25,100)).close().assemble()).push([(1,-64)]).circle(36).finalize().extrude(-7)).union(w1.sketch().arc((-18,-3),(-10,-22),(10,-23)).arc((32,-26),(48,-10)).segment((48,-15)).segment((100,-15)).segment((100,15)).segment((48,15)).segment((48,1)).arc((15,20),(-18,-3)).assemble().finalize().extrude(-6))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00756797.step')
