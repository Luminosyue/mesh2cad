import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,87))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-93,37),(70,-71),(-19,98)).arc((-10,80),(-10,60)).segment((1,60)).segment((1,43)).segment((-18,43)).arc((-56,18),(-93,37)).assemble().finalize().extrude(-187).union(w1.workplane(offset=-159/2).cylinder(159,100))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__137209_c0c9a7dd_0001.step')
