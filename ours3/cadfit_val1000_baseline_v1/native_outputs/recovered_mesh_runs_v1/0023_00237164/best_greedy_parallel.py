import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.3641, 0.1424, -0.13768), normal=(0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.81776, -1.00033)
loop_1 = loop_1.lineTo(0.81776, -1.3641)
loop_1 = loop_1.lineTo(0.39335, -1.3641)
loop_1 = loop_1.lineTo(0.39335, -1.00033)
loop_1 = loop_1.lineTo(0.8098, -1.00033)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.26), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.31171, 0.63622)
loop_1 = loop_1.circle(0.36369)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.52)

result = solid_1
result = result.add(solid_2)