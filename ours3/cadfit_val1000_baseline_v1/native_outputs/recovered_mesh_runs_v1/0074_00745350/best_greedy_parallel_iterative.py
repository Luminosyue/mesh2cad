import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.05042, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.01681)
loop_1 = loop_1.lineTo(-1.0, -0.01681)
loop_1 = loop_1.lineTo(1.0, -0.01143)
loop_1 = loop_1.lineTo(1.0, 0.01681)
loop_1 = loop_1.lineTo(-0.99864, 0.01681)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
