import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03806, 0.00176, 0.85978), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00176, 0.94044)
loop_1 = loop_1.circle(0.02146)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.72)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.85989), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.0, -0.9785)
loop_1 = loop_1.circle(0.02145)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.72)

result = solid_1
result = result.add(solid_2)