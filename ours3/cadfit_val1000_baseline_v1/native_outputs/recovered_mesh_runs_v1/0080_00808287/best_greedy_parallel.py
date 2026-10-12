import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.21603, 0.286, 0.21043), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.20089, 0.61375)
loop_1 = loop_1.lineTo(0.20089, -0.63447)
loop_1 = loop_1.lineTo(-0.19627, -0.63447)
loop_1 = loop_1.lineTo(-0.19627, 0.61375)
loop_1 = loop_1.lineTo(0.18498, 0.61375)
loop_1 = loop_1.lineTo(0.20089, 0.61375)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.12)

result = solid_1