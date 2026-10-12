import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01381, -0.00484, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00484, -0.01381)
loop_1 = loop_1.circle(0.13167)
loop_2 = sketch_1.moveTo(0.00484, -0.01381)
loop_2 = loop_2.circle(0.11348)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
