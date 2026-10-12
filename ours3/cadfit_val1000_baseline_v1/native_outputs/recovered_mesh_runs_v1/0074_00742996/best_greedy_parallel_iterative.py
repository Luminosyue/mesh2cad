import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00032, -0.36636, 0.2625), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.1815, 1.2625)
loop_1 = loop_1.lineTo(-0.18377, 0.17159)
loop_1 = loop_1.lineTo(-0.54513, 0.17159)
loop_1 = loop_1.lineTo(-0.54513, -0.7375)
loop_1 = loop_1.lineTo(0.54578, -0.7375)
loop_1 = loop_1.lineTo(0.5435, 0.17159)
loop_1 = loop_1.lineTo(0.18214, 0.17159)
loop_1 = loop_1.lineTo(0.17987, 1.2625)
loop_1 = loop_1.lineTo(-0.17809, 1.2625)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
