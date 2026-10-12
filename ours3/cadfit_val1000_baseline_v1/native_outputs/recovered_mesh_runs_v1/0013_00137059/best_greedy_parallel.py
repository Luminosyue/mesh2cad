import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.10578, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.1553)
loop_1 = loop_1.lineTo(-0.86348, 0.15127)
loop_1 = loop_1.lineTo(-0.99898, 0.02107)
loop_1 = loop_1.lineTo(-0.86705, -0.11536)
loop_1 = loop_1.lineTo(1.0, -0.15091)
loop_1 = loop_1.lineTo(1.0, 0.15383)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)
plane_2 = cq.Plane(origin=(-0.10422, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(1.0, 0.1553)
loop_1 = loop_1.lineTo(0.99853, -0.15527)
loop_1 = loop_1.lineTo(-0.87406, -0.11101)
loop_1 = loop_1.lineTo(-0.99893, 0.02316)
loop_1 = loop_1.lineTo(-0.85626, 0.1553)
loop_1 = loop_1.lineTo(0.99853, 0.1553)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.21)

result = solid_1
result = result.add(solid_2)