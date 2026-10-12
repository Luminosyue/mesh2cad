import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06216, -0.30664, -0.00629), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.06216, 0.03003)
loop_1 = loop_1.lineTo(0.93784, 0.03003)
loop_1 = loop_1.lineTo(0.93784, -0.0426)
loop_1 = loop_1.lineTo(0.56493, -0.0426)
loop_1 = loop_1.lineTo(0.56493, -0.01839)
loop_1 = loop_1.lineTo(-0.68926, -0.01839)
loop_1 = loop_1.lineTo(-0.68926, -0.0426)
loop_1 = loop_1.lineTo(-1.06216, -0.0426)
loop_1 = loop_1.lineTo(-1.06216, 0.00753)
loop_1 = loop_1.lineTo(-1.06216, 0.03003)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.66)

result = solid_1
