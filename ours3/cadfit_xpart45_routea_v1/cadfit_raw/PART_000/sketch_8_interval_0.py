import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04357, 0.1668, 0.0098), normal=(0.99979, 0.00071, -0.0203), xDir=(0.00071, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.16598, 0.01395)
loop_1 = loop_1.threePointArc((1.16577, 0.00335), (1.16573, -0.00682))
loop_1 = loop_1.lineTo(1.1453, -0.0273)
loop_1 = loop_1.threePointArc((1.13358, -0.02619), (1.1223, -0.02554))
loop_1 = loop_1.lineTo(1.09711, -0.02557)
loop_1 = loop_1.lineTo(1.0763, -0.02562)
loop_1 = loop_1.lineTo(1.0648, -0.02531)
loop_1 = loop_1.lineTo(1.01611, -0.00772)
loop_1 = loop_1.threePointArc((1.00616, -0.0084), (0.99579, -0.00903))
loop_1 = loop_1.lineTo(0.97074, -0.00436)
loop_1 = loop_1.lineTo(0.96128, 0.01615)
loop_1 = loop_1.lineTo(1.16598, 0.01395)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_000/sketch_8_interval_0.stl')