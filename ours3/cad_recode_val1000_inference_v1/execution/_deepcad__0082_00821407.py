import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((9,-2),(8,0),(9,1)).arc((-9,2),(9,-2)).assemble().push([(5,0)]).circle(4,mode='s').finalize().extrude(-200).union(w0.workplane(offset=-69/2).moveTo(0,0).cylinder(69,2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00821407.step')
