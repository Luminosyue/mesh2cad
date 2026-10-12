import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0011, -1.0, -0.00415), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0022, -0.00415)
loop_1 = loop_1.circle(0.03484)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
