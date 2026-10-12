import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-94))
r=w0.workplane(offset=-6/2).moveTo(0,0).cylinder(6,22).union(w0.sketch().arc((11,-14),(22,-3),(19,10)).arc((-4,3),(11,-14)).assemble().finalize().extrude(194)).union(w0.workplane(offset=194/2).moveTo(8,0).cylinder(194,13))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00581356.step')
