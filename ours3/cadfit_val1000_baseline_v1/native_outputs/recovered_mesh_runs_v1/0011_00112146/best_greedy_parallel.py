import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.02058), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, -0.0)
loop_1 = loop_1.lineTo(-0.92042, -0.38786)
loop_1 = loop_1.lineTo(-0.70193, -0.71056)
loop_1 = loop_1.lineTo(-0.37658, -0.92509)
loop_1 = loop_1.lineTo(0.00611, -0.99878)
loop_1 = loop_1.lineTo(0.38786, -0.92042)
loop_1 = loop_1.lineTo(0.71057, -0.70193)
loop_1 = loop_1.lineTo(0.92509, -0.37658)
loop_1 = loop_1.lineTo(0.99879, 0.00611)
loop_1 = loop_1.lineTo(0.92042, 0.38786)
loop_1 = loop_1.lineTo(0.70193, 0.71056)
loop_1 = loop_1.lineTo(0.37658, 0.92509)
loop_1 = loop_1.lineTo(-0.00611, 0.99878)
loop_1 = loop_1.lineTo(-0.38786, 0.92042)
loop_1 = loop_1.lineTo(-0.71057, 0.70193)
loop_1 = loop_1.lineTo(-0.92509, 0.37658)
loop_1 = loop_1.lineTo(-0.9996, 0.00203)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.0, 0.0)
loop_2 = loop_2.circle(0.1234)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.04)

result = solid_1