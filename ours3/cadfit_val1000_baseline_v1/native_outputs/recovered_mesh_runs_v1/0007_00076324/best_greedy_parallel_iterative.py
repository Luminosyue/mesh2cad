import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81336, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.27749)
loop_1 = loop_1.lineTo(0.9983, -0.27749)
loop_1 = loop_1.lineTo(-1.0, -0.27237)
loop_1 = loop_1.lineTo(-0.9983, 0.27749)
loop_1 = loop_1.lineTo(0.9983, 0.27749)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.63)

result = solid_1
