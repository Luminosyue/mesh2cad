import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, 0.00825, -0.00315), normal=(1.0, 0.0, -0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00825, -0.00326)
loop_1 = loop_1.circle(0.40992)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
