import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00362, 1.00063, -0.00196), normal=(0.00031, -1.0, 0.00016), xDir=(-1.0, -0.00031, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13521, 0.54945)
loop_1 = loop_1.threePointArc((-0.00523, 0.54568), (-0.14, 0.5405))
loop_1 = loop_1.lineTo(-0.15352, 0.52478)
loop_1 = loop_1.lineTo(-0.15273, -0.54449)
loop_1 = loop_1.lineTo(-0.13924, -0.55142)
loop_1 = loop_1.threePointArc((-0.00052, -0.55187), (0.13561, -0.5528))
loop_1 = loop_1.lineTo(0.14742, -0.53504)
loop_1 = loop_1.lineTo(0.14505, 0.54487)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
