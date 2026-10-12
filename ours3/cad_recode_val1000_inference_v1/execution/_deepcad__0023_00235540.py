import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,56))
w1=cq.Workplane('XY',origin=(0,0,35))
r=w0.sketch().arc((-92,-40),(-61,-57),(-59,-89)).arc((74,67),(-92,-40)).assemble().push([(-16,26)]).circle(52,mode='s').finalize().extrude(-112).union(w1.sketch().arc((-92,-40),(14,14),(75,-70)).arc((16,98),(-92,-40)).assemble().finalize().extrude(-77))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00235540.step')
