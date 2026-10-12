import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-95,0,0))
w1=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-2,1),(-1,-2)).segment((2,-1)).segment((1,2)).close().assemble().finalize().extrude(191).union(w1.workplane(offset=-10/2).moveTo(-93,0).cylinder(10,6))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00508197.step')
