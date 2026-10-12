import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.workplane(offset=-134/2).cylinder(134,15).union(w1.sketch().arc((-15,3),(14,-6),(-14,6)).arc((-11,3),(-15,3)).assemble().finalize().extrude(-200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00262307.step')
