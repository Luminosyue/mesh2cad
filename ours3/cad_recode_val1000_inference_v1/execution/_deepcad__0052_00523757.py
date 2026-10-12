import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-97,0))
r=w0.sketch().arc((-1,-13),(0,-7),(1,-13)).arc((1,13),(-1,-13)).assemble().circle(7,mode='s').finalize().extrude(200).union(w1.sketch().arc((-1,-7),(0,-6),(1,-7)).arc((0,7),(-1,-7)).assemble().finalize().extrude(41))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00523757.step')
