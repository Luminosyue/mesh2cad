import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-95))
r=w0.workplane(offset=147/2).cylinder(147,3).union(w1.sketch().circle(3).circle(2,mode='s').finalize().extrude(195))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0003_00037793.step')
