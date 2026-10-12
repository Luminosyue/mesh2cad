import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(5,0,0))
r=w0.sketch().segment((-100,-1),(-90,-5)).segment((-90,7)).segment((100,7)).segment((100,8)).segment((-90,8)).segment((-90,7)).segment((-92,7)).close().assemble().finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0054_00542891.step')
