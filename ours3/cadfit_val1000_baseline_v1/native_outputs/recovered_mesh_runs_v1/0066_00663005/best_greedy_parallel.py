import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.41936, 0.03226)
loop_1 = loop_1.lineTo(-1.0, 0.02839)
loop_1 = loop_1.lineTo(-0.99901, -0.03226)
loop_1 = loop_1.lineTo(0.41936, -0.02838)
loop_1 = loop_1.lineTo(0.41936, 0.03129)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)
plane_2 = cq.Plane(origin=(-0.04061, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.41936, 0.03226)
loop_1 = loop_1.lineTo(0.41837, -0.03226)
loop_1 = loop_1.lineTo(-1.0, -0.02927)
loop_1 = loop_1.lineTo(-0.99901, 0.03226)
loop_1 = loop_1.lineTo(0.41837, 0.03226)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.08)

result = solid_1
result = result.add(solid_2)