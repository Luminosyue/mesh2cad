import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00262, -0.96305, -0.21772), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99738, 0.64199)
loop_1 = loop_1.lineTo(-0.99738, -0.17096)
loop_1 = loop_1.lineTo(-0.32832, -0.17096)
loop_1 = loop_1.lineTo(-0.32832, -1.07743)
loop_1 = loop_1.lineTo(0.31917, -1.07743)
loop_1 = loop_1.lineTo(0.31917, -0.17096)
loop_1 = loop_1.lineTo(1.00262, -0.17096)
loop_1 = loop_1.lineTo(1.00262, 0.64199)
loop_1 = loop_1.lineTo(-0.98713, 0.64199)
loop_1 = loop_1.lineTo(-0.99738, 0.64199)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.92)

result = solid_1
