import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02768, 0.01677, 0.09473), normal=(0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01677, -0.02839)
loop_1 = loop_1.circle(0.99946)
loop_2 = sketch_1.moveTo(0.01674, -0.02843)
loop_2 = loop_2.circle(0.85659)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.19)
plane_2 = cq.Plane(origin=(-0.01697, 0.00499, -0.09473), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.00499, -0.01768)
loop_1 = loop_1.circle(0.99946)
loop_2 = sketch_2.moveTo(-0.00496, -0.01773)
loop_2 = loop_2.circle(0.85659)
sketch_2=sketch_2.add(loop_1).add(loop_2)
solid_2 = sketch_2.extrude(0.19)

result = solid_1
result = result.add(solid_2)