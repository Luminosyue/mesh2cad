import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.36515), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.48251, 1.0)
loop_1 = loop_1.lineTo(-0.47856, -1.0)
loop_1 = loop_1.lineTo(0.48251, -0.99605)
loop_1 = loop_1.lineTo(0.47856, 1.0)
loop_1 = loop_1.lineTo(-0.48054, 1.0)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.38918, 0.90455)
loop_2 = loop_2.lineTo(0.38918, 0.9011)
loop_2 = loop_2.lineTo(0.38573, -0.90455)
loop_2 = loop_2.lineTo(-0.38918, -0.9011)
loop_2 = loop_2.lineTo(-0.38918, 0.90283)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
