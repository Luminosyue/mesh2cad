import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.12592, -0.11963, -0.3065), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.88037, 0.68623)
loop_1 = loop_1.lineTo(-0.88037, -0.93808)
loop_1 = loop_1.lineTo(0.64149, -0.93808)
loop_1 = loop_1.lineTo(0.64149, 0.68623)
loop_1 = loop_1.lineTo(-0.84864, 0.68623)
loop_1 = loop_1.lineTo(-0.88037, 0.68623)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.48)
plane_2 = cq.Plane(origin=(0.24621, 0.56571, 0.17011), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.04385, -0.08769)
loop_1 = loop_1.circle(0.47754)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.14)

result = solid_1
result = result.add(solid_2)