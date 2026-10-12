import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00204, -0.05846, -0.00028), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.12512, 0.99972)
loop_1 = loop_1.lineTo(0.12104, 0.99972)
loop_1 = loop_1.lineTo(0.12104, -1.00028)
loop_1 = loop_1.lineTo(-0.12512, -1.00028)
loop_1 = loop_1.lineTo(-0.12512, 0.97715)
loop_1 = loop_1.lineTo(-0.12512, 0.99972)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.04819, 0.69203)
loop_2 = loop_2.circle(0.04557)
loop_3 = sketch_1.moveTo(-0.04819, -0.69259)
loop_3 = loop_3.circle(0.04557)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3)
solid_1 = sketch_1.extrude(0.12)

result = solid_1
