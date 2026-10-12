import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.03, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.88292, 0.0)
loop_1 = loop_1.circle(0.11729)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)
plane_2 = cq.Plane(origin=(0.0, -0.03, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.88292, 0.0)
loop_1 = loop_1.circle(0.11729)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.06)

result = solid_1
result = result.add(solid_2)