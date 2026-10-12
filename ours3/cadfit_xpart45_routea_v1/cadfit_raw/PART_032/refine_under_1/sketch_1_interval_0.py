import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07602, 0.91475, -0.06846), normal=(4e-05, -0.99993, 0.01141), xDir=(-1.0, -4e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14958, -0.25739)
loop_1 = loop_1.lineTo(-0.23758, -0.25738)
loop_1 = loop_1.lineTo(-0.22652, -0.25974)
loop_1 = loop_1.lineTo(-0.20426, -0.26326)
loop_1 = loop_1.lineTo(-0.18902, -0.26712)
loop_1 = loop_1.lineTo(-0.15738, -0.27109)
loop_1 = loop_1.lineTo(-0.1457, -0.27388)
loop_1 = loop_1.lineTo(-0.1105, -0.27577)
loop_1 = loop_1.lineTo(-0.09984, -0.27765)
loop_1 = loop_1.lineTo(-0.06296, -0.27947)
loop_1 = loop_1.lineTo(-0.05292, -0.28115)
loop_1 = loop_1.lineTo(-0.01673, -0.28262)
loop_1 = loop_1.lineTo(0.01947, -0.28043)
loop_1 = loop_1.threePointArc((0.03604, -0.27473), (0.0495, -0.27025))
loop_1 = loop_1.lineTo(0.07714, -0.26495)
loop_1 = loop_1.lineTo(0.10761, -0.2574)
loop_1 = loop_1.lineTo(-0.1461, -0.25739)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_1_interval_0.stl')