import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.44654, 0.09326)
loop_1 = loop_1.circle(0.07433)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.27296, 0.86854)
loop_1 = loop_1.circle(0.13091)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.02)

result = solid_1
result = result.add(solid_2)