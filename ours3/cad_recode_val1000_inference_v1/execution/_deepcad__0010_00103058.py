import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-33,0))
r=w0.sketch().arc((-100,-1),(18,-96),(83,42)).segment((83,48)).segment((80,48)).arc((72,61),(63,73)).arc((30,36),(39,92)).arc((-49,85),(-96,10)).arc((-84,1),(-100,-1)).assemble().push([(-14,-21)]).circle(49,mode='s').finalize().extrude(29).union(w0.sketch().segment((-97,-15),(-52,28)).segment((-52,26)).segment((-13,26)).segment((-13,69)).segment((-15,69)).segment((-15,71)).segment((-52,71)).segment((-52,69)).arc((-88,46),(-97,6)).close().assemble().reset().face(w0.sketch().arc((-17,-97),(10,-70),(44,-72)).segment((44,-81)).segment((49,-81)).segment((49,-71)).arc((85,-50),(97,-12)).segment((100,-1)).segment((97,0)).arc((61,77),(-17,96)).segment((-17,71)).segment((13,71)).segment((13,69)).segment((-17,69)).segment((-17,26)).segment((13,26)).segment((13,-13)).segment((-12,-13)).segment((-12,-3)).segment((-17,-3)).close().assemble()).finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00103058.step')
