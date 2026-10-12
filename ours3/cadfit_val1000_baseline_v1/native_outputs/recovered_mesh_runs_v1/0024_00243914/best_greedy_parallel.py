import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.12), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4, 0.04)
loop_1 = loop_1.lineTo(-0.39901, -0.04)
loop_1 = loop_1.lineTo(1.0, -0.037)
loop_1 = loop_1.lineTo(0.99901, 0.04)
loop_1 = loop_1.lineTo(-0.39901, 0.04)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.12), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.4, 0.04)
loop_1 = loop_1.lineTo(-0.39901, -0.04)
loop_1 = loop_1.lineTo(1.0, -0.03704)
loop_1 = loop_1.lineTo(0.999, 0.04)
loop_1 = loop_1.lineTo(-0.39901, 0.04)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.24)

result = solid_1
result = result.add(solid_2)