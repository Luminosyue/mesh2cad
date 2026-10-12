import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,6))
r=w0.sketch().segment((-100,-3),(-93,-3)).segment((-93,-7)).segment((100,-7)).segment((100,7)).segment((-93,7)).segment((-93,3)).segment((-100,3)).close().assemble().finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00489189.step')
