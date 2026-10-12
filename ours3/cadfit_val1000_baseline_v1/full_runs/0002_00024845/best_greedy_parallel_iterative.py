import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01592, 0.00085, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10085, 0.11592)
loop_1 = loop_1.lineTo(-0.10085, -0.08408)
loop_1 = loop_1.lineTo(0.09915, -0.08408)
loop_1 = loop_1.lineTo(0.09915, 0.11592)
loop_1 = loop_1.lineTo(-0.09687, 0.11592)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.00085, 0.01592)
loop_2 = loop_2.circle(0.08398)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1