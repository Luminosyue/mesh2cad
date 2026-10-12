import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.67333, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94636, 1.0)
loop_1 = loop_1.lineTo(0.94391, 0.21032)
loop_1 = loop_1.lineTo(0.27867, 0.20809)
loop_1 = loop_1.lineTo(-0.2846, -1.0)
loop_1 = loop_1.lineTo(-0.94636, -0.99755)
loop_1 = loop_1.lineTo(-0.94146, 1.0)
loop_1 = loop_1.lineTo(0.94391, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.34)

result = solid_1
