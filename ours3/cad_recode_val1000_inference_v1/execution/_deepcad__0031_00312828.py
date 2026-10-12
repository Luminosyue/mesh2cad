import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(0,0,0))
r=w0.sketch().segment((-1,-100),(1,10)).segment((0,10)).segment((0,-91)).segment((0,-92)).segment((-1,-92)).close().assemble().reset().face(w0.sketch().segment((0,38),(1,38)).segment((0,42)).close().assemble()).reset().face(w0.sketch().segment((-1,92),(0,83)).segment((0,100)).close().assemble()).finalize().extrude(0)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00312828.step')
