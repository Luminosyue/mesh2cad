import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.64419, -0.00651, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00605, -0.0037)
loop_1 = loop_1.circle(0.1481)
loop_2 = sketch_1.moveTo(0.00605, -0.00369)
loop_2 = loop_2.circle(0.08639)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.25)
plane_2 = cq.Plane(origin=(0.64419, -0.00651, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00696, 1.29207)
loop_1 = loop_1.circle(0.14807)
loop_2 = sketch_2.moveTo(0.00696, 1.29207)
loop_2 = loop_2.circle(0.08638)
sketch_2=sketch_2.add(loop_1).add(loop_2)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)