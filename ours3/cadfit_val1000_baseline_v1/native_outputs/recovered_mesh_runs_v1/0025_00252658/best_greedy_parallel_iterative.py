import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.11346, 0.2486, 1.0), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.71919, -0.02522)
loop_1 = loop_1.lineTo(0.71919, -0.20169)
loop_1 = loop_1.lineTo(-0.04552, -0.20169)
loop_1 = loop_1.lineTo(-0.04662, -0.87816)
loop_1 = loop_1.lineTo(-0.22199, -0.87816)
loop_1 = loop_1.lineTo(-0.21923, 0.65125)
loop_1 = loop_1.lineTo(-0.04552, 0.65125)
loop_1 = loop_1.lineTo(-0.04552, -0.02522)
loop_1 = loop_1.lineTo(0.71202, -0.02522)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
