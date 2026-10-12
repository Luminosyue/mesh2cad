import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().circle(6).circle(4,mode='s').finalize().extrude(-200).union(w0.sketch().arc((-3,4),(0,-5),(3,4)).arc((0,3),(-3,4)).assemble().finalize().extrude(-67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0009_00093295.step')
