import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-86))
w1=cq.Workplane('XY',origin=(0,0,-84))
r=w0.workplane(offset=170/2).moveTo(98,0).cylinder(170,2).union(w1.workplane(offset=170/2).moveTo(-98,0).cylinder(170,2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00623202.step')
