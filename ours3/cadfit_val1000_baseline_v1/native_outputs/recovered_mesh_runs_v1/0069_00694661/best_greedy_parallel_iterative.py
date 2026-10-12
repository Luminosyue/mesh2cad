import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07253, 0.22926, -0.05444), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.22926, 0.57253)
loop_1 = loop_1.lineTo(-1.22926, -0.42747)
loop_1 = loop_1.lineTo(0.77074, -0.42747)
loop_1 = loop_1.lineTo(0.77074, 0.57253)
loop_1 = loop_1.lineTo(-1.19953, 0.57253)
loop_1 = loop_1.lineTo(-1.22926, 0.57253)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.11815, 0.07253)
loop_2 = loop_2.circle(0.07131)
loop_3 = sketch_1.moveTo(0.10407, 0.32808)
loop_3 = loop_3.circle(0.06582)
loop_4 = sketch_1.moveTo(0.65963, 0.32808)
loop_4 = loop_4.circle(0.06582)
sketch_1=sketch_1.add(loop_1).add(loop_2).add(loop_3).add(loop_4)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
