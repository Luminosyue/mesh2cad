import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.59, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31557, 1.0)
loop_1 = loop_1.lineTo(-0.42517, 0.99849)
loop_1 = loop_1.lineTo(-0.42066, -1.0)
loop_1 = loop_1.lineTo(-0.31557, -0.99851)
loop_1 = loop_1.lineTo(-0.31404, -0.77778)
loop_1 = loop_1.lineTo(-0.17853, -0.77628)
loop_1 = loop_1.lineTo(-0.18155, -0.33333)
loop_1 = loop_1.lineTo(-0.31557, -0.33181)
loop_1 = loop_1.lineTo(-0.31557, 0.99849)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.19)

result = solid_1
