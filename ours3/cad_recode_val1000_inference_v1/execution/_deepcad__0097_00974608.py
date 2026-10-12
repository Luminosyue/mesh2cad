import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,75,0))
r=w0.sketch().segment((-95,27),(-61,74)).arc((-84,51),(-95,27)).assemble().reset().face(w0.sketch().arc((-73,-14),(-69,-21),(-65,-28)).segment((-65,-39)).segment((-62,-39)).arc((-44,-60),(-18,-72)).close().assemble()).reset().face(w0.sketch().segment((-54,82),(-7,73)).arc((45,59),(75,12)).segment((100,-1)).arc((55,81),(-39,90)).arc((-46,87),(-54,82)).assemble()).reset().face(w0.sketch().arc((-35,-93),(-21,-88),(-8,-99)).arc((38,-92),(72,-69)).segment((37,-62)).arc((10,-73),(-17,-71)).close().assemble()).finalize().extrude(-150).union(w0.sketch().push([(-60,-3)]).circle(39).circle(37,mode='s').finalize().extrude(-118))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00974608.step')
