import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08724, 0.05043, 1.0), normal=(0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49488, 0.69054)
loop_1 = loop_1.lineTo(0.49488, -0.86501)
loop_1 = loop_1.lineTo(0.05043, -0.8664)
loop_1 = loop_1.lineTo(0.05043, -1.08724)
loop_1 = loop_1.lineTo(-0.39401, -1.08724)
loop_1 = loop_1.lineTo(-0.39401, 0.91276)
loop_1 = loop_1.lineTo(0.05043, 0.91138)
loop_1 = loop_1.lineTo(0.05043, 0.69054)
loop_1 = loop_1.lineTo(0.4921, 0.69054)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
