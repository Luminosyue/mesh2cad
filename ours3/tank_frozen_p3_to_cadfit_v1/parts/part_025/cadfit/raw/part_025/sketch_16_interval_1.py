import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08748, -0.04441, 0.21623), normal=(0.00771, 0.03914, -0.9992), xDir=(0.0, -0.99923, -0.03914))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09565, 0.65265)
loop_1 = loop_1.lineTo(-0.10256, 0.6259)
loop_1 = loop_1.lineTo(-0.1332, 0.60807)
loop_1 = loop_1.lineTo(-0.1611, 0.62278)
loop_1 = loop_1.lineTo(-0.17191, 0.65201)
loop_1 = loop_1.lineTo(-0.1776, 0.67878)
loop_1 = loop_1.lineTo(-0.1623, 0.70043)
loop_1 = loop_1.threePointArc((-0.14871, 0.70401), (-0.13578, 0.70609))
loop_1 = loop_1.lineTo(-0.10719, 0.68467)
loop_1 = loop_1.threePointArc((-0.09941, 0.66687), (-0.096, 0.654))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.54)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/tank_frozen_p3_to_cadfit_v1/parts/part_025/cadfit/raw/part_025/sketch_16_interval_1.stl')