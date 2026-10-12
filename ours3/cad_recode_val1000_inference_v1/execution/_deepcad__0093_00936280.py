import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,60))
w1=cq.Workplane('XY',origin=(0,0,52))
r=w0.sketch().arc((-91,-41),(15,19),(-59,-81)).arc((61,-79),(93,37)).segment((93,36)).segment((89,36)).segment((89,45)).segment((90,45)).arc((80,60),(65,75)).arc((11,21),(23,97)).arc((-77,64),(-91,-41)).assemble().finalize().extrude(-120).union(w1.sketch().arc((-43,91),(15,-99),(0,100)).arc((-19,98),(-43,91)).assemble().finalize().extrude(-99))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00936280.step')
