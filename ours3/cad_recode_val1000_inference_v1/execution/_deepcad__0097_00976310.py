import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-25,0))
r=w0.sketch().segment((-21,-100),(13,-100)).segment((-16,-93)).segment((-11,-74)).segment((21,-83)).segment((21,100)).segment((-21,100)).segment((-21,58)).arc((-19,57),(-21,56)).close().assemble().reset().face(w0.sketch().segment((-11,23),(11,23)).segment((11,30)).arc((0,27),(-11,30)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-11,82),(0,85),(11,82)).segment((11,89)).segment((-11,89)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-21,-100),(13,-100)).segment((13,-93)).arc((-4,-96),(-21,-93)).close().assemble()).reset().face(w0.sketch().arc((17,42),(19,41),(21,40)).segment((21,42)).close().assemble()).finalize().extrude(49)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0097_00976310.step')
