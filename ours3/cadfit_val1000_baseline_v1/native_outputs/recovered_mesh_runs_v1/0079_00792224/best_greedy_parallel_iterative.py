import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33221, -0.17037)
loop_1 = loop_1.lineTo(-0.99664, -0.17303)
loop_1 = loop_1.lineTo(-0.99398, -0.83479)
loop_1 = loop_1.lineTo(0.33221, -0.83214)
loop_1 = loop_1.lineTo(0.33221, -0.1717)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.64)
plane_2 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.99664, 0.83509)
loop_1 = loop_1.lineTo(-0.33221, 0.83242)
loop_1 = loop_1.lineTo(-0.32955, 0.16479)
loop_1 = loop_1.lineTo(0.99664, 0.16746)
loop_1 = loop_1.lineTo(0.99664, 0.83375)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)