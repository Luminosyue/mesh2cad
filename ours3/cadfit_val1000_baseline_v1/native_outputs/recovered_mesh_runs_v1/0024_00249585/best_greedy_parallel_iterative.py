import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0426, 0.00947, -0.06489), normal=(-0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.91693, 1.0426)
loop_1 = loop_1.lineTo(-0.91577, 0.0426)
loop_1 = loop_1.lineTo(-0.91417, 0.02697)
loop_1 = loop_1.lineTo(-0.91417, -0.9574)
loop_1 = loop_1.lineTo(0.89522, -0.9574)
loop_1 = loop_1.lineTo(0.89637, 0.0426)
loop_1 = loop_1.lineTo(0.89798, 0.05822)
loop_1 = loop_1.lineTo(0.89798, 1.0426)
loop_1 = loop_1.lineTo(-0.91087, 1.0426)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
