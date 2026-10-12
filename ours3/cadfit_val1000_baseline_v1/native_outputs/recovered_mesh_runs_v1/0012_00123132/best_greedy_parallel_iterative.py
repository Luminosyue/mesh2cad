import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00284, -1.0, -0.00135), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00284, -0.00135)
loop_1 = loop_1.circle(0.48176)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
