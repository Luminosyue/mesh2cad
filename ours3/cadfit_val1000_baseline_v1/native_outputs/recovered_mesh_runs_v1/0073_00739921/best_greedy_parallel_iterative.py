import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02328, 0.21059, 0.38435), normal=(0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21059, 0.02328)
loop_1 = loop_1.circle(0.99987)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
