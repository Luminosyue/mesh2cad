import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.4), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.6, 1.0)
loop_1 = loop_1.lineTo(-0.59798, 0.6)
loop_1 = loop_1.lineTo(-0.19936, 0.59808)
loop_1 = loop_1.lineTo(0.2, -0.6101)
loop_1 = loop_1.lineTo(0.20202, -1.0)
loop_1 = loop_1.lineTo(0.6, -0.99798)
loop_1 = loop_1.lineTo(0.59596, 1.0)
loop_1 = loop_1.lineTo(-0.59798, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
