import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,40))
r=w0.sketch().segment((-100,-100),(-47,-100)).segment((-100,27)).close().assemble().reset().face(w0.sketch().segment((-100,41),(24,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-24,-100),(100,-100)).segment((100,100)).segment((47,100)).segment((100,-27)).close().assemble()).finalize().extrude(-80).union(w0.sketch().segment((-88,-27),(-68,-27)).arc((0,-70),(68,-27)).segment((88,-27)).segment((88,27)).segment((68,27)).arc((0,70),(-68,27)).segment((-88,27)).close().assemble().finalize().extrude(-80))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00478579.step')
