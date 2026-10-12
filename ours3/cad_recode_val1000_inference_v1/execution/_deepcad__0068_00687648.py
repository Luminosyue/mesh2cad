import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.workplane(offset=197/2).cylinder(197,4).union(w0.workplane(offset=200/2).cylinder(200,4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00687648.step')
