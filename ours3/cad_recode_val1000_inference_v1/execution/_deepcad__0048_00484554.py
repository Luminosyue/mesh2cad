import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,-57)).segment((-98,-57)).segment((-98,-60)).segment((-100,-60)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-60,57),(-57,57)).arc((0,-71),(57,57)).segment((60,57)).segment((60,64)).segment((46,64)).arc((0,77),(-46,64)).segment((-60,64)).close().assemble().finalize().extrude(-4))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00484554.step')
