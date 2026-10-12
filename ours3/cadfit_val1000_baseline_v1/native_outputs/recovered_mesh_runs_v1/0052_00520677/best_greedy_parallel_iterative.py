import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.87767, -0.27936, -0.4), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27936, 0.87768)
loop_1 = loop_1.circle(0.99992)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.8)

result = solid_1
