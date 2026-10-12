import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01339, -0.02287, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22436, 0.07139)
loop_1 = loop_1.lineTo(-0.20441, 0.03054)
loop_1 = loop_1.lineTo(-0.17776, -0.0063)
loop_1 = loop_1.lineTo(-0.14522, -0.03804)
loop_1 = loop_1.lineTo(-0.10772, -0.06376)
loop_1 = loop_1.lineTo(-0.06529, -0.08297)
loop_1 = loop_1.lineTo(-0.02242, -0.09427)
loop_1 = loop_1.lineTo(0.02287, -0.09817)
loop_1 = loop_1.lineTo(0.06817, -0.09427)
loop_1 = loop_1.lineTo(0.11213, -0.08268)
loop_1 = loop_1.lineTo(0.15347, -0.06376)
loop_1 = loop_1.lineTo(0.19096, -0.03804)
loop_1 = loop_1.lineTo(0.22351, -0.0063)
loop_1 = loop_1.lineTo(0.25015, 0.03054)
loop_1 = loop_1.lineTo(0.2701, 0.07139)
loop_1 = loop_1.lineTo(-0.21818, 0.07139)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
