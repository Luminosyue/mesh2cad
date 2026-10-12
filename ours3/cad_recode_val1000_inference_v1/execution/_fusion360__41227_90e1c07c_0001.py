import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-92,0))
r=w0.workplane(offset=152/2).cylinder(152,22).union(w1.sketch().arc((-21,7),(16,-15),(-10,20)).arc((-11,18),(-12,17)).arc((15,-14),(-19,8)).arc((-20,7),(-21,7)).assemble().finalize().extrude(192))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__41227_90e1c07c_0001.step')
