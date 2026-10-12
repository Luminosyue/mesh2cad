import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06769, -0.38471, -0.07844), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80887, 0.39803)
loop_1 = loop_1.lineTo(0.80887, 0.18038)
loop_1 = loop_1.lineTo(-0.93231, 0.17863)
loop_1 = loop_1.lineTo(-0.93169, -0.55491)
loop_1 = loop_1.lineTo(-0.67349, -0.55377)
loop_1 = loop_1.lineTo(-0.67349, -0.07844)
loop_1 = loop_1.lineTo(1.06769, -0.0773)
loop_1 = loop_1.lineTo(1.06707, 0.39803)
loop_1 = loop_1.lineTo(0.81229, 0.39803)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.77)

result = solid_1
