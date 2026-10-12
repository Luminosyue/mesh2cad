import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-67,0))
w1=cq.Workplane('ZX',origin=(0,-38,0))
r=w0.sketch().segment((-89,-59),(-73,-59)).arc((-84,0),(-73,59)).segment((-89,59)).close().assemble().reset().face(w0.sketch().segment((55,-78),(100,-78)).segment((100,78)).segment((55,78)).segment((55,34)).arc((-45,0),(55,-33)).close().assemble()).finalize().extrude(114).union(w1.sketch().segment((-100,-78),(-55,-78)).segment((-55,-33)).segment((55,-33)).segment((55,-78)).segment((100,-78)).segment((100,78)).segment((55,78)).segment((55,33)).segment((-55,33)).segment((-55,78)).segment((-100,78)).close().assemble().finalize().extrude(105))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00307721.step')
