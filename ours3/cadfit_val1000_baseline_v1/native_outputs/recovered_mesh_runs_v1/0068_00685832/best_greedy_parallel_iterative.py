import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 1.0)
loop_1 = loop_1.lineTo(-0.99734, 0.0)
loop_1 = loop_1.lineTo(-0.0, -0.00266)
loop_1 = loop_1.lineTo(0.00266, -1.0)
loop_1 = loop_1.lineTo(1.0, -0.99734)
loop_1 = loop_1.lineTo(0.99468, 1.0)
loop_1 = loop_1.lineTo(-0.99733, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
