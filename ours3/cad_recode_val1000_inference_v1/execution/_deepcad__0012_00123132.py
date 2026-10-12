import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-87,0))
r=w0.sketch().arc((-41,25),(-47,-11),(-26,-41)).arc((-25,-39),(-23,-42)).arc((48,0),(-23,42)).arc((-33,35),(-41,25)).assemble().finalize().extrude(120).union(w1.sketch().arc((-40,-27),(33,35),(-27,-40)).arc((-19,-40),(-13,-37)).arc((30,31),(-38,-13)).arc((-42,-20),(-40,-27)).assemble().finalize().extrude(187))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00123132.step')
