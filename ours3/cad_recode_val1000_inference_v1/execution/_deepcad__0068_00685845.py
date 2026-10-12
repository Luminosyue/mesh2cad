import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-97,58),(-50,58)).segment((-50,46)).arc((-42,42),(-34,37)).segment((-73,73)).close().assemble().reset().face(w0.sketch().arc((-31,-37),(-10,-51),(13,-58)).segment((13,-46)).arc((10,-42),(13,-37)).close().assemble()).reset().face(w0.sketch().segment((-13,13),(13,-13)).segment((13,13)).close().assemble()).finalize().extrude(147).union(w0.sketch().segment((-100,-96),(-91,-96)).segment((-91,-100)).segment((93,-100)).segment((-100,100)).close().assemble().reset().face(w0.sketch().segment((32,-100),(91,-100)).segment((91,-96)).segment((100,-96)).segment((100,-90)).close().assemble()).finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00685845.step')
