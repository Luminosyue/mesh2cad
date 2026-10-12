import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.03), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 1.0)
loop_1 = loop_1.lineTo(-0.99467, -1.0)
loop_1 = loop_1.lineTo(1.0, -0.99467)
loop_1 = loop_1.lineTo(0.99466, 0.23077)
loop_1 = loop_1.lineTo(0.23077, 0.23344)
loop_1 = loop_1.lineTo(0.2281, 1.0)
loop_1 = loop_1.lineTo(-0.99734, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
