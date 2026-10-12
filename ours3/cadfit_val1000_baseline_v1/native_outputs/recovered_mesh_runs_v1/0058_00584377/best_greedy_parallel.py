import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.62, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23523, -0.11692)
loop_1 = loop_1.lineTo(0.23658, 0.11692)
loop_1 = loop_1.lineTo(-0.47536, 0.11489)
loop_1 = loop_1.lineTo(-0.47401, -0.11692)
loop_1 = loop_1.lineTo(0.23456, -0.11692)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.78)

result = solid_1