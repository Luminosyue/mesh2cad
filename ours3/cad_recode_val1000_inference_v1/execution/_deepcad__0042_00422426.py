import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
r=w0.sketch().segment((-91,-83),(-33,-83)).segment((-33,-33)).segment((33,-33)).segment((33,33)).segment((-33,33)).segment((-33,83)).segment((-91,83)).close().assemble().finalize().extrude(24).union(w0.sketch().segment((-100,-100),(-52,-100)).segment((-33,-73)).segment((-33,-10)).segment((-14,-34)).segment((33,-34)).segment((33,33)).segment((100,33)).segment((100,100)).segment((44,100)).arc((43,98),(42,100)).segment((-100,100)).close().assemble().reset().face(w0.sketch().segment((-100,-100),(-52,-100)).segment((-100,-61)).close().assemble()).reset().face(w0.sketch().segment((-100,-59),(-99,-58)).segment((-100,-58)).close().assemble()).finalize().extrude(134))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00422426.step')
