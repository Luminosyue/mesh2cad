import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0055, 0.03675, -0.30643), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66175, 1.0055)
loop_1 = loop_1.lineTo(-0.66175, -0.9945)
loop_1 = loop_1.lineTo(0.58825, -0.9945)
loop_1 = loop_1.lineTo(0.58825, 1.0055)
loop_1 = loop_1.lineTo(-0.62898, 1.0055)
loop_1 = loop_1.lineTo(-0.66175, 1.0055)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.59032, 0.93407)
loop_2 = loop_2.lineTo(0.51682, 0.93407)
loop_2 = loop_2.lineTo(0.51682, -0.92307)
loop_2 = loop_2.lineTo(-0.59032, -0.92307)
loop_2 = loop_2.lineTo(-0.59032, 0.90348)
loop_2 = loop_2.lineTo(-0.59032, 0.93407)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
