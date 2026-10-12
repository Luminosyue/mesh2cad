import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,-57)).arc((-96,-60),(-100,-63)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-57,57),(-55,57)).arc((0,96),(55,57)).segment((57,57)).arc((0,97),(-57,57)).assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00645024.step')
