import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,94))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().rect(20,20).circle(9,mode='s').finalize().extrude(-192).union(w1.sketch().arc((-8,10),(-9,0),(-5,-10)).segment((5,-10)).arc((6,0),(10,10)).close().assemble().finalize().extrude(-200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00024845.step')
