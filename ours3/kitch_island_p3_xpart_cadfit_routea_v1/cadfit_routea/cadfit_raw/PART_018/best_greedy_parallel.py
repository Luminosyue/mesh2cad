import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07086, 0.05103)
loop_1 = loop_1.lineTo(-0.07056, -0.04051)
loop_1 = loop_1.lineTo(-0.07042, -0.17779)
loop_1 = loop_1.lineTo(-0.05942, -0.2152)
loop_1 = loop_1.lineTo(-0.04529, -0.22846)
loop_1 = loop_1.lineTo(-0.00473, -0.23235)
loop_1 = loop_1.lineTo(0.03089, -0.23189)
loop_1 = loop_1.lineTo(0.05851, -0.21431)
loop_1 = loop_1.lineTo(0.06877, -0.18319)
loop_1 = loop_1.lineTo(0.07038, 0.04247)
loop_1 = loop_1.lineTo(0.07022, 0.10351)
loop_1 = loop_1.threePointArc((0.07051, 0.13672), (0.07026, 0.16824))
loop_1 = loop_1.threePointArc((0.06795, 0.18625), (0.0654, 0.20311))
loop_1 = loop_1.lineTo(0.02951, 0.23022)
loop_1 = loop_1.lineTo(-0.01031, 0.22985)
loop_1 = loop_1.lineTo(-0.04591, 0.2258)
loop_1 = loop_1.lineTo(-0.06583, 0.20248)
loop_1 = loop_1.lineTo(-0.07044, 0.1623)
loop_1 = loop_1.threePointArc((-0.07057, 0.10779), (-0.07086, 0.0514))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1