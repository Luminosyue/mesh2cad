import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.08), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.4)
loop_1 = loop_1.lineTo(-0.99627, -0.4)
loop_1 = loop_1.lineTo(1.0, -0.39441)
loop_1 = loop_1.lineTo(0.99627, 0.4)
loop_1 = loop_1.lineTo(-0.99813, 0.4)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
