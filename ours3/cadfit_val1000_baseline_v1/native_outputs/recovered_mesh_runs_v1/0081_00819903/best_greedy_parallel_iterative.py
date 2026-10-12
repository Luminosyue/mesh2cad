import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.13667), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.33333)
loop_1 = loop_1.lineTo(-0.99657, -0.33333)
loop_1 = loop_1.lineTo(1.0, -0.32819)
loop_1 = loop_1.lineTo(0.99714, 0.06857)
loop_1 = loop_1.lineTo(0.59485, 0.33333)
loop_1 = loop_1.lineTo(-0.99828, 0.33333)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
