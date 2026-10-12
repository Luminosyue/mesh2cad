import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-92,0))
r=w0.workplane(offset=151/2).cylinder(151,21).union(w0.workplane(offset=200/2).cylinder(200,17)).union(w1.sketch().arc((-19,9),(17,-12),(-14,15)).arc((-14,10),(-19,9)).assemble().finalize().extrude(143))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00788724.step')
