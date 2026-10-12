import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-74))
w1=cq.Workplane('YZ',origin=(-63,0,0))
r=w0.sketch().segment((-95,10),(-26,31)).arc((-61,54),(-82,88)).arc((-91,73),(-95,55)).close().assemble().reset().face(w0.sketch().arc((-95,-79),(-35,-90),(22,-58)).segment((-46,-58)).segment((-46,-51)).arc((-71,-60),(-95,-51)).close().assemble()).reset().face(w0.sketch().arc((28,-58),(30,-60),(32,-62)).segment((32,-58)).close().assemble()).finalize().extrude(148).union(w1.sketch().segment((-90,-52),(-89,-52)).segment((-89,-35)).arc((-60,-51),(-29,-52)).segment((-29,-44)).arc((-42,-18),(-26,0)).arc((-26,2),(-25,4)).arc((-25,5),(-26,5)).arc((-27,5),(-29,6)).segment((-29,74)).segment((95,74)).segment((95,73)).segment((100,73)).segment((100,71)).segment((95,71)).segment((95,74)).segment((-90,74)).segment((-90,27)).arc((-100,0),(-90,-27)).close().assemble().finalize().extrude(-32))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00193178.step')
