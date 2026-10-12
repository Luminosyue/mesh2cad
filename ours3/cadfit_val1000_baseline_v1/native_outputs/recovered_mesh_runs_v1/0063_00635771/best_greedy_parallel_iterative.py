import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31579, -0.23231, -0.34894), normal=(-0.0, 1.0, 0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58503, 0.03568)
loop_1 = loop_1.lineTo(0.58503, -0.00279)
loop_1 = loop_1.lineTo(1.16195, -0.00279)
loop_1 = loop_1.lineTo(1.16195, -1.31048)
loop_1 = loop_1.lineTo(0.0081, -1.31048)
loop_1 = loop_1.lineTo(0.0081, -0.65663)
loop_1 = loop_1.lineTo(-0.03036, -0.65663)
loop_1 = loop_1.lineTo(-0.03036, -1.34894)
loop_1 = loop_1.lineTo(1.20041, -1.34894)
loop_1 = loop_1.lineTo(1.20041, 0.03568)
loop_1 = loop_1.lineTo(0.62139, 0.03568)
loop_1 = loop_1.lineTo(0.58503, 0.03568)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)

result = solid_1
