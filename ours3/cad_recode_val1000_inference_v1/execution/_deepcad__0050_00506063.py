import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-57))
w1=cq.Workplane('XY',origin=(0,0,-54))
r=w0.sketch().segment((-19,45),(-18,45)).arc((-49,-3),(-11,-47)).segment((-11,-48)).segment((-10,-48)).arc((3,-49),(15,-46)).segment((16,-46)).segment((16,-45)).arc((47,13),(-10,48)).segment((-11,48)).segment((-12,47)).arc((-15,47),(-18,45)).close().assemble().finalize().extrude(-43).union(w0.sketch().segment((14,-17),(14,-15)).segment((16,-15)).segment((16,-19)).arc((23,21),(14,-17)).assemble().finalize().extrude(157)).union(w1.workplane(offset=107/2).moveTo(28,-1).cylinder(107,21))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00506063.step')
