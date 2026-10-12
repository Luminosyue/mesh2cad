import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,-50)).segment((25,-50)).segment((25,50)).segment((100,50)).segment((100,100)).segment((-100,100)).segment((-100,50)).segment((-25,50)).segment((-25,-50)).segment((-100,-50)).close().assemble().finalize().extrude(-200)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0024_00247039.step')
