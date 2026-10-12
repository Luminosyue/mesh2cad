import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,29))
r=w0.sketch().segment((-47,-18),(-41,-27)).segment((-31,-18)).close().assemble().reset().face(w0.sketch().segment((-43,24),(-12,28)).segment((-12,31)).segment((1,31)).segment((30,39)).arc((-10,48),(-43,24)).assemble()).reset().face(w0.sketch().arc((4,-49),(14,-47),(23,-44)).segment((13,-29)).close().assemble()).reset().face(w0.sketch().segment((24,23),(48,-11)).arc((46,18),(24,41)).close().assemble()).finalize().extrude(-172).union(w0.sketch().arc((-33,2),(-32,0),(-32,-2)).segment((-27,-2)).segment((-27,-19)).segment((-32,-19)).arc((-32,-21),(-31,-23)).segment((-26,-19)).close().assemble().finalize().extrude(-35)).union(w0.sketch().segment((-47,19),(-23,35)).arc((-35,28),(-47,19)).assemble().finalize().extrude(-37)).union(w1.sketch().arc((-38,-33),(-33,-37),(-27,-41)).arc((-18,-46),(-6,-49)).arc((18,-46),(39,-33)).segment((31,-33)).arc((32,-26),(31,-19)).segment((39,-19)).arc((35,-11),(29,-4)).arc((28,-18),(22,-31)).segment((22,-33)).segment((20,-33)).arc((13,-34),(6,-33)).close().assemble().reset().face(w1.sketch().segment((-43,25),(43,25)).arc((0,43),(-43,25)).assemble()).finalize().extrude(-129))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0089_00894529.step')
