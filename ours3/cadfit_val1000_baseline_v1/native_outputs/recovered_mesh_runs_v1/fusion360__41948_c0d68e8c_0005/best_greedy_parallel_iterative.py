import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.1), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0, -0.00071)
loop_1 = loop_1.circle(0.99941)
loop_2 = sketch_1.moveTo(1e-05, -0.00072)
loop_2 = loop_2.circle(0.85652)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
