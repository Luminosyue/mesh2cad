import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-43,0))
r=w0.sketch().segment((-71,-70),(-31,-98)).segment((-28,-93)).segment((-28,-28)).segment((-60,-10)).segment((-71,-28)).close().assemble().reset().face(w0.sketch().segment((28,-28),(60,-46)).segment((71,-28)).close().assemble()).finalize().extrude(6).union(w0.sketch().segment((-86,-100),(-29,-100)).segment((-29,-43)).segment((44,-43)).arc((43,-41),(43,-39)).segment((29,-39)).segment((29,14)).segment((-86,14)).close().assemble().reset().face(w0.sketch().arc((28,100),(29,93),(29,86)).segment((29,14)).segment((28,14)).close().assemble()).reset().face(w0.sketch().segment((29,100),(86,100)).segment((86,86)).arc((86,93),(85,100)).close().assemble()).finalize().extrude(86))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0080_00804081.step')
