import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.17064, 0.08352, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08352, -0.17064)
loop_1 = loop_1.circle(0.74991)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
