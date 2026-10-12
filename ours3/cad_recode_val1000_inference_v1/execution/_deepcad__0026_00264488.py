import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,27))
r=w0.sketch().segment((-100,-59),(-53,-59)).segment((-53,-58)).segment((-34,-58)).segment((-34,-59)).segment((100,-59)).segment((100,59)).segment((-100,59)).close().assemble().push([(10,-48)]).circle(10,mode='s').push([(0,0)]).circle(36,mode='s').finalize().extrude(-55).union(w0.sketch().segment((-90,-17),(-83,-17)).segment((-83,-58)).segment((-60,-58)).arc((-69,0),(-31,45)).segment((-90,45)).close().assemble().reset().face(w0.sketch().arc((31,-45),(69,0),(90,58)).segment((31,58)).close().assemble()).finalize().extrude(-54))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00264488.step')
