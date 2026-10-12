import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,93,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().circle(12).circle(10,mode='s').finalize().extrude(-193).union(w1.sketch().arc((-12,-1),(-10,-2),(-11,-4)).arc((11,3),(-12,-1)).assemble().finalize().extrude(-157))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0069_00697517.step')
