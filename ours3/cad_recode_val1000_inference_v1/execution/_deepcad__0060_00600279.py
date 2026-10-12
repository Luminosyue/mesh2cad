import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,62))
r=w0.workplane(offset=-189/2).cylinder(189,28).union(w0.workplane(offset=-44/2).cylinder(44,29)).union(w1.workplane(offset=-162/2).cylinder(162,28))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00600279.step')
