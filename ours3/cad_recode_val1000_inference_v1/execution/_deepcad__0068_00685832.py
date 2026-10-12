import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('ZX',origin=(0,0,0))
r=w0.sketch().segment((-100,-100),(0,-100)).segment((0,-58)).segment((-100,-18)).close().assemble().reset().face(w0.sketch().segment((-100,18),(0,-18)).segment((0,0)).segment((100,0)).segment((100,100)).segment((-100,100)).close().assemble()).finalize().extrude(-200).union(w1.sketch().segment((-87,-23),(-50,-23)).segment((-50,0)).segment((92,0)).segment((92,13)).segment((-50,13)).segment((-50,23)).segment((-87,23)).close().assemble().finalize().extrude(-28))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00685832.step')
