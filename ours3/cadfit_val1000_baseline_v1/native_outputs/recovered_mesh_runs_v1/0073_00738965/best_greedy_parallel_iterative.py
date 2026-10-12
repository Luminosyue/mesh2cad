import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00194, -0.05, -0.01417), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00194, -0.01417)
loop_1 = loop_1.circle(0.99984)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
