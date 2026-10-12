import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
r=w0.sketch().segment((-93,-34),(-93,-27)).segment((-77,-27)).segment((-77,-52)).segment((-81,-52)).arc((-62,-77),(-35,-93)).segment((-35,-94)).segment((-32,-94)).arc((-2,-100),(28,-94)).segment((37,-94)).segment((37,-92)).arc((87,-47),(92,22)).segment((93,22)).segment((93,39)).segment((90,39)).arc((82,54),(72,67)).segment((72,43)).segment((34,43)).segment((34,23)).arc((55,-10),(34,-42)).segment((34,-45)).segment((-4,-45)).segment((-4,-42)).arc((-45,-3),(-17,48)).arc((-15,50),(-12,52)).arc((-10,53),(-8,53)).segment((65,53)).segment((65,75)).segment((34,75)).segment((34,84)).arc((25,91),(15,97)).segment((-61,77)).segment((-46,60)).arc((-95,24),(-93,-34)).assemble().reset().face(w0.sketch().arc((-41,34),(-38,26),(-38,18)).arc((-37,26),(-41,34)).assemble(),mode='s').reset().face(w0.sketch().segment((-35,-94),(-15,-94)).segment((-15,-92)).arc((-25,-89),(-35,-84)).close().assemble(),mode='s').finalize().extrude(-14)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00987356.step')
