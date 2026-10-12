import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.15651), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.93746, -0.37628)
loop_1 = loop_1.lineTo(-0.13911, -0.99849)
loop_1 = loop_1.lineTo(0.79517, -0.61972)
loop_1 = loop_1.lineTo(0.93428, 0.37877)
loop_1 = loop_1.lineTo(0.13911, 0.99849)
loop_1 = loop_1.lineTo(-0.79517, 0.61972)
loop_1 = loop_1.lineTo(-0.93717, -0.37428)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
