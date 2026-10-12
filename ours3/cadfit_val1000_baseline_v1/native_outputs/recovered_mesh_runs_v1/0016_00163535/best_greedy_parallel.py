import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.70455), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0, 0.0)
loop_1 = loop_1.circle(0.99979)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)
plane_2 = cq.Plane(origin=(0.54441, 0.0337, 0.11455), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.0337, -0.09196)
loop_1 = loop_1.circle(0.36358)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.59)
plane_3 = cq.Plane(origin=(0.0, 0.0, -0.61), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_3 = cq.Workplane(plane_3)
loop_1 = sketch_3.moveTo(-0.0, -0.09091)
loop_1 = loop_1.circle(0.9089)
sketch_3=sketch_3.add(loop_1)
solid_3 = sketch_3.extrude(0.73)

result = solid_1
result = result.add(solid_2)
result = result.add(solid_3)