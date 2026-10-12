import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06579, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01316, 1.0)
loop_1 = loop_1.lineTo(-0.01316, 1.0)
loop_1 = loop_1.lineTo(-0.00762, -1.0)
loop_1 = loop_1.lineTo(0.01316, -1.0)
loop_1 = loop_1.lineTo(0.01316, 0.99865)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1