import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83667, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08333, 1.0)
loop_1 = loop_1.lineTo(-0.08333, 0.99855)
loop_1 = loop_1.lineTo(-0.07902, -1.0)
loop_1 = loop_1.lineTo(0.08333, -0.99855)
loop_1 = loop_1.lineTo(0.08333, 0.99855)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
