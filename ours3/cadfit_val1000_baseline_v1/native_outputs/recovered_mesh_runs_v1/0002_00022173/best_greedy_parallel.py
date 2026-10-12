import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.2, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.19672, 1.0)
loop_1 = loop_1.lineTo(-0.56475, 0.84519)
loop_1 = loop_1.lineTo(-0.84122, 0.56592)
loop_1 = loop_1.lineTo(-0.98996, 0.20218)
loop_1 = loop_1.lineTo(-0.9884, -0.19079)
loop_1 = loop_1.lineTo(-0.83676, -0.55334)
loop_1 = loop_1.lineTo(-0.55808, -0.8304)
loop_1 = loop_1.lineTo(-0.18989, -0.98198)
loop_1 = loop_1.threePointArc((0.01702, -0.99995), (0.21293, -0.97693))
loop_1 = loop_1.lineTo(0.56829, -0.82353)
loop_1 = loop_1.lineTo(0.84357, -0.54308)
loop_1 = loop_1.lineTo(0.99077, -0.17871)
loop_1 = loop_1.lineTo(0.98754, 0.21425)
loop_1 = loop_1.lineTo(0.83436, 0.57615)
loop_1 = loop_1.lineTo(0.5545, 0.85203)
loop_1 = loop_1.lineTo(0.19044, 1.0)
loop_1 = loop_1.lineTo(-0.19463, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)

result = solid_1