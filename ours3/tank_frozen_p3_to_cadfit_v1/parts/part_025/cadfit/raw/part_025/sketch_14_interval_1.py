import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24861, 0.04844, 0.32811), normal=(0.00636, 0.22803, 0.97363), xDir=(0.0, 0.97365, -0.22803))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09416, 0.54285)
loop_1 = loop_1.lineTo(0.08284, 0.54993)
loop_1 = loop_1.lineTo(0.06368, 0.54285)
loop_1 = loop_1.lineTo(0.03282, 0.53908)
loop_1 = loop_1.lineTo(0.01749, 0.53494)
loop_1 = loop_1.lineTo(-0.00302, 0.51677)
loop_1 = loop_1.lineTo(-0.01166, 0.48709)
loop_1 = loop_1.lineTo(-0.00393, 0.45921)
loop_1 = loop_1.lineTo(0.01842, 0.44785)
loop_1 = loop_1.lineTo(0.04439, 0.4495)
loop_1 = loop_1.lineTo(0.0655, 0.45921)
loop_1 = loop_1.threePointArc((0.07094, 0.47049), (0.07539, 0.47974))
loop_1 = loop_1.threePointArc((0.08147, 0.4969), (0.08386, 0.50477))
loop_1 = loop_1.lineTo(0.08792, 0.51671)
loop_1 = loop_1.lineTo(0.08771, 0.5307)
loop_1 = loop_1.lineTo(0.09335, 0.54133)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_14_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_14_interval_1.stl')