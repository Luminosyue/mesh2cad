import cadquery as cq
import math


# Revolve operation 1
plane_1 = cq.Plane(origin=(-0.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.10763, -0.00086)
sketch_1 = sketch_1.lineTo(0.10839, -0.84261)
sketch_1 = sketch_1.threePointArc((0.10929, -0.88804), (0.10959, -0.93358))
sketch_1 = sketch_1.lineTo(0.1056, -0.9481)
sketch_1 = sketch_1.lineTo(0.09302, -0.95761)
sketch_1 = sketch_1.lineTo(0.07962, -0.9586)
sketch_1 = sketch_1.threePointArc((0.06418, -0.95487), (0.05088, -0.95167))
sketch_1 = sketch_1.threePointArc((0.03155, -0.95067), (0.01507, -0.95094))
sketch_1 = sketch_1.lineTo(-0.12163, -0.95137)
sketch_1 = sketch_1.threePointArc((-0.13148, -0.95216), (-0.14006, -0.95217))
sketch_1 = sketch_1.lineTo(-0.15175, -0.97266)
sketch_1 = sketch_1.lineTo(-0.1402, -0.98345)
sketch_1 = sketch_1.lineTo(-0.00328, -0.98505)
sketch_1 = sketch_1.lineTo(0.03067, -0.98602)
sketch_1 = sketch_1.threePointArc((0.05088, -0.98836), (0.06997, -0.99202))
sketch_1 = sketch_1.threePointArc((0.08551, -0.99417), (0.09898, -0.99412))
sketch_1 = sketch_1.lineTo(0.11928, -0.99403)
sketch_1 = sketch_1.lineTo(0.14134, -0.97681)
sketch_1 = sketch_1.threePointArc((0.14749, -0.96103), (0.14983, -0.95284))
sketch_1 = sketch_1.lineTo(0.15179, -0.91179)
sketch_1 = sketch_1.lineTo(0.15185, -0.00086)
sketch_1 = sketch_1.lineTo(0.10763, -0.00086)
sketch_1 = sketch_1.close()
solid_revolve_1 = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.098, 0.0, 0.001), axisEnd=(-0.902, 0.0, 0.001))

result = solid_revolve_1