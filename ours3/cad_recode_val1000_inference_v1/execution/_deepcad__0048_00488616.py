import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-95))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((4,3),(5,1),(6,2)).arc((5,2),(6,3)).arc((5,4),(4,3)).assemble().finalize().extrude(95).union(w0.workplane(offset=195/2).moveTo(-25,-9).cylinder(195,1)).union(w1.workplane(offset=48/2).moveTo(25,9).cylinder(48,1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00488616.step')
