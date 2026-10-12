import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.workplane(offset=200/2).cylinder(200,3).union(w0.sketch().arc((1,-3),(2,-2),(3,-1)).arc((2,0),(3,1)).arc((2,2),(1,3)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00323208.step')
