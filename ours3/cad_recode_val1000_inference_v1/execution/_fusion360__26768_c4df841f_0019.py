import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('YZ',origin=(-68,0,0))
r=w0.sketch().arc((-15,-4),(14,6),(-15,3)).arc((-13,1),(-15,-4)).assemble().finalize().extrude(97).union(w1.sketch().arc((-15,-4),(-10,-12),(-1,-15)).arc((1,-14),(2,-15)).arc((11,-11),(15,-3)).arc((14,-2),(16,-1)).arc((1,15),(-15,-1)).arc((-13,-2),(-15,-4)).assemble().finalize().extrude(168))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__26768_c4df841f_0019.step')
