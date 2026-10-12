import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.29321, -0.05257, -0.89111), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35483, 0.77469)
loop_1 = loop_1.lineTo(-0.35483, -0.70679)
loop_1 = loop_1.lineTo(0.45998, -0.70679)
loop_1 = loop_1.lineTo(0.45998, 0.77469)
loop_1 = loop_1.lineTo(-0.35457, 0.77469)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.26224, 0.66358)
loop_2 = loop_2.lineTo(0.36739, 0.66358)
loop_2 = loop_2.lineTo(0.36739, -0.59568)
loop_2 = loop_2.lineTo(-0.26224, -0.59568)
loop_2 = loop_2.lineTo(-0.26224, 0.64587)
loop_2 = loop_2.lineTo(-0.26224, 0.66358)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.78)

result = solid_1