import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-100,-1),(-98,-10)).segment((-52,-8)).segment((-52,-10)).segment((99,-10)).segment((99,-7)).segment((100,-7)).segment((99,1)).segment((99,8)).segment((96,8)).segment((96,10)).segment((27,10)).arc((28,7),(28,5)).segment((28,4)).segment((27,4)).arc((23,-1),(18,4)).segment((17,4)).segment((17,5)).arc((16,7),(15,8)).segment((14,8)).segment((14,10)).segment((-52,8)).segment((-52,6)).segment((-97,9)).arc((-97,4),(-96,-1)).close().assemble().finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00562187.step')
