import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().arc((-2,-2),(0,-2),(2,-1)).segment((1,2)).arc((-1,2),(-2,0)).segment((-1,-1)).close().assemble().finalize().extrude(200)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00021261.step')
