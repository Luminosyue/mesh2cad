import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05426, 0.26848, 0.0039), normal=(-0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94574, 0.65788)
loop_1 = loop_1.lineTo(0.66356, 0.65788)
loop_1 = loop_1.lineTo(0.66356, -0.65008)
loop_1 = loop_1.lineTo(0.94574, -0.65008)
loop_1 = loop_1.lineTo(0.94574, 0.64121)
loop_1 = loop_1.lineTo(0.94574, 0.65788)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)
plane_2 = cq.Plane(origin=(-0.05426, -0.70152, 0.0039), normal=(-0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.14348, 0.65788)
loop_1 = loop_1.lineTo(-1.05426, 0.65788)
loop_1 = loop_1.lineTo(-1.05426, -0.65008)
loop_1 = loop_1.lineTo(0.14348, -0.65008)
loop_1 = loop_1.lineTo(0.14348, 0.63328)
loop_1 = loop_1.lineTo(0.14348, 0.65788)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.16)

result = solid_1
result = result.add(solid_2)