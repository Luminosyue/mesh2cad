import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02549, -1.0, 0.00123), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01692, 0.00123)
loop_1 = loop_1.circle(0.69642)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.76)

result = solid_1
