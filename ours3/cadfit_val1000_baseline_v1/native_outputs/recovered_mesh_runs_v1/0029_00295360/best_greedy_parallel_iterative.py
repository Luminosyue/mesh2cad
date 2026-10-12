import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01749, -0.05624, -0.0009), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87498, 0.12813)
loop_1 = loop_1.lineTo(1.01749, 0.12813)
loop_1 = loop_1.lineTo(1.01749, -0.12994)
loop_1 = loop_1.lineTo(-0.89217, -0.12841)
loop_1 = loop_1.threePointArc((-0.96233, -0.08485), (-0.98073, -0.00124))
loop_1 = loop_1.threePointArc((-0.95891, 0.0876), (-0.87529, 0.12812))
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.84545, -0.0009)
loop_2 = loop_2.circle(0.06369)
loop_3 = sketch_1.moveTo(-0.87498, -0.0009)
loop_3 = loop_3.circle(0.02972)
loop_4 = sketch_1.moveTo(0.45835, -0.0009)
loop_4 = loop_4.circle(0.01911)
loop_5 = sketch_1.moveTo(0.6519, -0.0009)
loop_5 = loop_5.circle(0.01911)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4).add(loop_5)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
