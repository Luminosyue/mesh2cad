import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.workplane(offset=-200/2).moveTo(0,-1).cylinder(200,16).union(w1.sketch().arc((-12,13),(11,-14),(-7,16)).arc((-8,13),(-12,13)).assemble().finalize().extrude(-188))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00682640.step')
