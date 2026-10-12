import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,0)).segment((0,0)).segment((0,55)).arc((-1,56),(0,57)).segment((0,100)).segment((-100,100)).close().assemble().finalize().extrude(200)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0028_00283887.step')
