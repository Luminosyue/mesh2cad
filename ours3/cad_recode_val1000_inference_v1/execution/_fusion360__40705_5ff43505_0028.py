import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,56))
r=w0.sketch().circle(17).circle(12,mode='s').finalize().extrude(-180).union(w0.sketch().circle(24).rect(22,22,mode='s').finalize().extrude(-10)).union(w1.workplane(offset=-156/2).cylinder(156,17))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__40705_5ff43505_0028.step')
