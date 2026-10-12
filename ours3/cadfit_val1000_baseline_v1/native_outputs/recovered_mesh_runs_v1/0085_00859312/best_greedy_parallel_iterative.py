import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.3), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.59762, 1.0)
loop_1 = loop_1.lineTo(-0.59336, -1.0)
loop_1 = loop_1.lineTo(0.59762, -0.99574)
loop_1 = loop_1.lineTo(0.59336, 1.0)
loop_1 = loop_1.lineTo(-0.59549, 1.0)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.49597, 0.84605)
loop_2 = loop_2.lineTo(0.49597, 0.84247)
loop_2 = loop_2.lineTo(0.49239, -0.84605)
loop_2 = loop_2.lineTo(-0.49597, -0.84247)
loop_2 = loop_2.lineTo(-0.49597, 0.84426)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.6)

result = solid_1
