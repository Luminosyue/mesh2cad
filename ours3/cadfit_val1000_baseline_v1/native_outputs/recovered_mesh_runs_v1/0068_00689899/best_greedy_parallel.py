import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00915, -0.00992, 0.00415), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07733, -0.57643)
loop_1 = loop_1.circle(0.41433)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.46)
plane_2 = cq.Plane(origin=(0.00915, -0.00992, -0.16585), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00992, 0.41053)
loop_1 = loop_1.circle(0.41434)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.63)
plane_3 = cq.Plane(origin=(-0.2624, -0.00017, 0.00585), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_3 = cq.Workplane(plane_3)
loop_1 = sketch_3.moveTo(-0.00017, 0.23108)
loop_1 = loop_1.circle(0.50644)
sketch_3=sketch_3.add(loop_1)
solid_3 = sketch_3.extrude(0.47)

result = solid_1
result = result.add(solid_2)
result = result.add(solid_3)