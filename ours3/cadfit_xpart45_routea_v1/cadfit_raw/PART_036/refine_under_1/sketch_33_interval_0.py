import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.15568, 0.00745, -0.1122), normal=(-0.02791, 0.62791, -0.77778), xDir=(0.99901, 0.04441, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77722, 0.04926)
loop_1 = loop_1.lineTo(0.78813, 0.03808)
loop_1 = loop_1.lineTo(0.80287, 0.03575)
loop_1 = loop_1.lineTo(0.81315, 0.04076)
loop_1 = loop_1.threePointArc((0.81642, 0.04627), (0.81987, 0.05199))
loop_1 = loop_1.threePointArc((0.8196, 0.06059), (0.81935, 0.06765))
loop_1 = loop_1.lineTo(0.81821, 0.10217)
loop_1 = loop_1.lineTo(0.81824, 0.11354)
loop_1 = loop_1.lineTo(0.81828, 0.12445)
loop_1 = loop_1.lineTo(0.80239, 0.13039)
loop_1 = loop_1.lineTo(0.7923, 0.13038)
loop_1 = loop_1.lineTo(0.77357, 0.13036)
loop_1 = loop_1.lineTo(0.77331, 0.11945)
loop_1 = loop_1.lineTo(0.77315, 0.10485)
loop_1 = loop_1.lineTo(0.77351, 0.08268)
loop_1 = loop_1.lineTo(0.77308, 0.05367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_33_interval_0.stl')