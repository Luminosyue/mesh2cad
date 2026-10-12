import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.71932, -0.06993)
loop_1 = loop_1.lineTo(0.71932, -0.09624)
loop_1 = loop_1.lineTo(-0.47015, -0.09295)
loop_1 = loop_1.lineTo(-0.47015, -0.06993)
loop_1 = loop_1.lineTo(0.71851, -0.06993)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
