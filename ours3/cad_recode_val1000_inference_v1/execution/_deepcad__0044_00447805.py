import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,0),(-91,-4)).segment((-91,3)).segment((-1,3)).segment((-96,3)).close().assemble().reset().face(w0.sketch().segment((-87,-3),(47,-3)).segment((47,3)).segment((3,3)).close().assemble()).reset().face(w0.sketch().segment((51,-3),(87,-3)).segment((100,0)).segment((97,3)).segment((51,3)).close().assemble()).finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0044_00447805.step')
