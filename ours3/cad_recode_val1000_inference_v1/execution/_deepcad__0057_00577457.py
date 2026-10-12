import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-50))
r=w0.sketch().segment((-100,-100),(-62,-100)).segment((-100,-58)).close().assemble().reset().face(w0.sketch().segment((-100,-40),(-27,22)).segment((-27,13)).segment((19,13)).segment((19,27)).segment((-21,27)).segment((100,-32)).segment((100,78)).segment((57,78)).segment((57,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-10,-100),(100,-100)).segment((100,-53)).close().assemble()).finalize().extrude(100)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0057_00577457.step')
