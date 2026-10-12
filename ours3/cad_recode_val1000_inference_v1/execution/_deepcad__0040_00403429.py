import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-85))
r=w0.sketch().arc((-9,4),(-2,-4),(11,0)).segment((4,0)).segment((4,1)).segment((2,1)).segment((2,3)).close().assemble().finalize().extrude(2).union(w0.workplane(offset=118/2).cylinder(118,3)).union(w1.sketch().arc((-3,1),(2,-2),(-2,2)).arc((-2,1),(-3,1)).assemble().finalize().extrude(185))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00403429.step')
