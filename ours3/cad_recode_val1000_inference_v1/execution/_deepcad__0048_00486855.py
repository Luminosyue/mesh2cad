import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,47))
r=w0.sketch().segment((-100,-100),(-53,-100)).segment((-53,-96)).segment((-100,-65)).close().assemble().reset().face(w0.sketch().segment((-100,-33),(-53,-2)).segment((-53,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-48,-100),(100,-100)).segment((100,100)).segment((-5,100)).segment((74,50)).segment((1,-70)).segment((1,-100)).segment((-10,-100)).close().assemble()).finalize().extrude(-94)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00486855.step')
