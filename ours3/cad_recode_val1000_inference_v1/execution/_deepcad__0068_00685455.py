import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-91,-10),(-85,-10)).arc((0,-85),(85,-10)).segment((91,-10)).segment((91,10)).segment((85,10)).arc((0,85),(-85,10)).segment((-91,10)).close().assemble().finalize().extrude(4).union(w0.sketch().segment((-100,-100),(100,-100)).segment((100,97)).segment((84,97)).segment((84,100)).segment((-100,100)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00685455.step')
