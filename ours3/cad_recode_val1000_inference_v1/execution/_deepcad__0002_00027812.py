import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-75,0))
r=w0.sketch().segment((-100,-100),(-74,-100)).segment((-100,-57)).close().assemble().reset().face(w0.sketch().segment((-100,-42),(-99,-41)).segment((-100,-41)).close().assemble()).reset().face(w0.sketch().segment((-99,-100),(-71,-100)).segment((-99,-59)).close().assemble()).reset().face(w0.sketch().segment((-99,-10),(-10,-37)).segment((-25,-50)).segment((38,13)).segment((-99,13)).close().assemble()).finalize().extrude(113).union(w0.sketch().segment((-99,-100),(-71,-100)).segment((-52,-77)).segment((-99,-77)).close().assemble().reset().face(w0.sketch().segment((-100,-100),(-71,-100)).segment((-71,-96)).close().assemble()).reset().face(w0.sketch().segment((-55,32),(100,75)).segment((100,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-31,-10),(-20,-10)).segment((-20,10)).close().assemble()).reset().face(w0.sketch().segment((20,-10),(31,5)).segment((20,10)).close().assemble()).finalize().extrude(150))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00027812.step')
