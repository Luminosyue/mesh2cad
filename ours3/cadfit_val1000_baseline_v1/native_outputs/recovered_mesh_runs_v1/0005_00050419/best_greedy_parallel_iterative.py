import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.66793)
loop_1 = loop_1.lineTo(-0.99724, 0.02788)
loop_1 = loop_1.lineTo(0.43197, 0.03064)
loop_1 = loop_1.lineTo(0.4292, 0.66793)
loop_1 = loop_1.lineTo(-0.99862, 0.66793)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
