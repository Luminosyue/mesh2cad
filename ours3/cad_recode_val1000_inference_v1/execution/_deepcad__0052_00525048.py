import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-6,1),(-5,1)).segment((-5,-2)).segment((4,-2)).segment((4,1)).segment((6,1)).segment((6,2)).arc((0,-3),(-6,2)).close().assemble().finalize().extrude(173).union(w0.sketch().arc((-4,-3),(0,-2),(4,-3)).segment((4,3)).segment((-4,3)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00525048.step')
