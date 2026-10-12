import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.71), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95106, 0.61803)
loop_1 = loop_1.lineTo(-0.94714, -0.61931)
loop_1 = loop_1.lineTo(0.22694, -0.99667)
loop_1 = loop_1.lineTo(0.94863, 0.00333)
loop_1 = loop_1.lineTo(0.2206, 0.99873)
loop_1 = loop_1.lineTo(-0.9491, 0.61867)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.10041, 0.0)
loop_2 = loop_2.circle(0.11197)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.42)

result = solid_1
