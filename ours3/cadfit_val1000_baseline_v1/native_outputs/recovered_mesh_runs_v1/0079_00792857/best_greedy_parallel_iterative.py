import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.86, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00762, 0.14476)
loop_1 = loop_1.lineTo(-0.00762, 0.14456)
loop_1 = loop_1.lineTo(-0.00701, -0.14476)
loop_1 = loop_1.lineTo(0.00762, -0.14456)
loop_1 = loop_1.lineTo(0.00762, 0.14456)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)

result = solid_1
