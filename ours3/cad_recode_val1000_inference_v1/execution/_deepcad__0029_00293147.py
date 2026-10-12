import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,78,0))
r=w0.sketch().segment((-100,-78),(85,-78)).segment((85,-62)).segment((100,-62)).segment((100,78)).segment((59,78)).arc((29,10),(-1,78)).segment((-100,78)).close().assemble().finalize().extrude(-156).union(w0.sketch().segment((-92,-36),(-40,-55)).segment((-40,-25)).segment((11,-25)).segment((11,-63)).segment((92,-63)).segment((92,63)).segment((-40,63)).segment((-40,40)).segment((-56,40)).segment((-56,38)).segment((-40,38)).segment((-40,36)).segment((-56,36)).segment((-56,34)).segment((-60,34)).close().assemble().finalize().extrude(-10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0029_00293147.step')
