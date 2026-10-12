import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-13,0))
r=w0.sketch().segment((-100,-13),(100,-13)).segment((100,13)).segment((-100,13)).segment((-100,10)).arc((-96,8),(-100,6)).close().assemble().finalize().extrude(26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0085_00859602.step')
