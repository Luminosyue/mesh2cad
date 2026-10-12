import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().arc((-82,57),(-90,-43),(-4,-100)).segment((-4,-99)).segment((-1,-99)).segment((-1,-100)).arc((13,-99),(27,-96)).segment((19,-96)).segment((19,-77)).arc((-15,-23),(37,-62)).segment((69,-62)).segment((69,-72)).arc((93,-36),(100,7)).segment((95,7)).segment((95,-11)).segment((37,-11)).segment((37,7)).segment((24,7)).segment((24,44)).segment((37,44)).segment((37,62)).segment((77,62)).arc((19,98),(-52,86)).arc((-57,76),(-69,73)).arc((-76,64),(-82,57)).assemble().reset().face(w0.sketch().arc((-92,40),(-90,-43),(-19,-72)).segment((-19,-77)).segment((-15,-77)).segment((-15,-72)).arc((37,-46),(37,11)).segment((-15,11)).segment((-15,17)).segment((-19,17)).segment((-19,11)).segment((-52,11)).arc((-73,28),(-92,40)).assemble(),mode='s').finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00504080.step')
