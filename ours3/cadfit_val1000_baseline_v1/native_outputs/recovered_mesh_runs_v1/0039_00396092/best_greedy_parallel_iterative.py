import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.14782, 0.06338, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.06338, -0.14782)
loop_1 = loop_1.circle(0.66659)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
