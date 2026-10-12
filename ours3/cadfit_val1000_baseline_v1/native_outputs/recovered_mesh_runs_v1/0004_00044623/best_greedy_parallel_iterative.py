import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.66667, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.5)
loop_1 = loop_1.lineTo(-0.99621, -0.5)
loop_1 = loop_1.lineTo(-0.33333, -0.4981)
loop_1 = loop_1.lineTo(-0.32967, 0.14371)
loop_1 = loop_1.lineTo(0.98673, 0.5)
loop_1 = loop_1.lineTo(-0.9981, 0.5)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
