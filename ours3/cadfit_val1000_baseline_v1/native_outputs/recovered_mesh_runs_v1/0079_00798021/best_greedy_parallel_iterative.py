import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.32, -0.00077, 0.01435), normal=(-1.0, 0.0, -0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01733, 0.12748)
loop_1 = loop_1.lineTo(-0.01733, 0.0596)
loop_1 = loop_1.lineTo(-0.31598, 0.0596)
loop_1 = loop_1.lineTo(-0.31598, -0.07614)
loop_1 = loop_1.lineTo(0.31751, -0.07614)
loop_1 = loop_1.lineTo(0.31751, 0.0596)
loop_1 = loop_1.lineTo(0.00077, 0.06005)
loop_1 = loop_1.lineTo(0.00032, 0.12748)
loop_1 = loop_1.lineTo(-0.01721, 0.12748)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.32)

result = solid_1
