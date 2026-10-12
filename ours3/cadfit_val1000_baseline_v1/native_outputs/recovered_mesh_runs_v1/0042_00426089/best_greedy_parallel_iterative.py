import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06233, 0.00053, -0.05495), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00512, 1.06233)
loop_1 = loop_1.lineTo(-0.00341, -0.93767)
loop_1 = loop_1.lineTo(0.00234, 1.06233)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.05505), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.00459, 1.0)
loop_1 = loop_1.lineTo(0.00066, -1.0)
loop_1 = loop_1.lineTo(-0.00066, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.11)

result = solid_1
result = result.add(solid_2)