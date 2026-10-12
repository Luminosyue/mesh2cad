import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(51,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.workplane(offset=-151/2).cylinder(151,8).union(w1.workplane(offset=-91/2).cylinder(91,11))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00199854.step')
