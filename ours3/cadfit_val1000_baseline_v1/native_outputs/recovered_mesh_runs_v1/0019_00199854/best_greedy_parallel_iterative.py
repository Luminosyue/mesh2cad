import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.0, -0.00679, -0.0019), normal=(1.0, -0.0, 0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00679, -0.00228)
loop_1 = loop_1.circle(0.1115)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
