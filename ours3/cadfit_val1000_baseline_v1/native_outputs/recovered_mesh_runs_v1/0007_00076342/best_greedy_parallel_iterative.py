import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.91304, 0.02899)
loop_1 = loop_1.lineTo(0.91179, -0.02899)
loop_1 = loop_1.lineTo(-0.91304, -0.02415)
loop_1 = loop_1.lineTo(-0.91179, 0.02899)
loop_1 = loop_1.lineTo(0.91179, 0.02899)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
