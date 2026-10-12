import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17143, 0.71429)
loop_1 = loop_1.lineTo(-0.20952, 0.71429)
loop_1 = loop_1.lineTo(-0.20494, -1.0)
loop_1 = loop_1.lineTo(-0.17143, -1.0)
loop_1 = loop_1.lineTo(-0.17143, 0.71312)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.52)
plane_2 = cq.Plane(origin=(-0.73524, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.17143, 0.71429)
loop_1 = loop_1.lineTo(-0.17617, -1.0)
loop_1 = loop_1.lineTo(-0.20952, -1.0)
loop_1 = loop_1.lineTo(-0.20478, 0.71429)
loop_1 = loop_1.lineTo(-0.17263, 0.71429)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.53)

result = solid_1
result = result.add(solid_2)