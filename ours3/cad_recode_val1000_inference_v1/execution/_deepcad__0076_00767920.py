import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-10,0))
w1=cq.Workplane('ZX',origin=(0,-9,0))
r=w0.sketch().segment((-99,67),(-47,8)).segment((-43,11)).segment((-95,69)).close().assemble().reset().face(w0.sketch().segment((-56,91),(-33,67)).segment((-25,62)).segment((-33,73)).segment((-45,79)).segment((-45,80)).segment((-46,80)).segment((-55,94)).close().assemble()).reset().face(w0.sketch().segment((-26,-12),(-18,-21)).arc((-16,-23),(-14,-25)).segment((-9,-30)).segment((-7,-28)).segment((-14,-25)).arc((-15,-23),(-17,-21)).segment((-25,-10)).close().assemble()).reset().face(w0.sketch().segment((-11,45),(29,9)).segment((30,10)).segment((-9,47)).close().assemble()).reset().face(w0.sketch().arc((1,-40),(18,-57),(40,-71)).arc((82,-49),(96,-92)).arc((90,-56),(60,-33)).arc((30,-57),(1,-36)).close().assemble()).finalize().extrude(19).union(w1.sketch().arc((-99,66),(-96,60),(-92,55)).arc((-89,89),(-55,94)).arc((-77,96),(-94,83)).arc((-97,75),(-99,66)).assemble().finalize().extrude(18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0076_00767920.step')
