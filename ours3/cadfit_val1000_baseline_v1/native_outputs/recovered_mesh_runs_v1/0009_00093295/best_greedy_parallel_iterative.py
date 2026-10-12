import cadquery as cq
import math

plane_1 = cq.Plane(origin=(1.0, 0.00214, -0.00365), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00214, -0.00365)
loop_1 = loop_1.circle(0.05532)
loop_2 = sketch_1.moveTo(-0.00214, -0.00365)
loop_2 = loop_2.circle(0.03688)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
