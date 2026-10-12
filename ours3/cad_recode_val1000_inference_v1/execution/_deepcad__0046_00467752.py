import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-67,0,0))
r=w0.workplane(offset=-33/2).cylinder(33,6).union(w0.sketch().arc((4,0),(6,0),(6,1)).segment((5,1)).arc((5,0),(4,0)).assemble().finalize().extrude(162)).union(w0.workplane(offset=167/2).moveTo(5,0).cylinder(167,1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00467752.step')
