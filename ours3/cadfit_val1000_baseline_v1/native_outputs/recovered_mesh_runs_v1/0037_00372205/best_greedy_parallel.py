import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3005, -0.01691, -0.00197), normal=(-1.0, -0.0, 0.0), xDir=(-0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98309, 0.17984)
loop_1 = loop_1.lineTo(1.01691, 0.17984)
loop_1 = loop_1.lineTo(1.01691, -0.18379)
loop_1 = loop_1.lineTo(-0.98309, -0.18379)
loop_1 = loop_1.lineTo(-0.98309, 0.1556)
loop_1 = loop_1.lineTo(-0.98309, 0.17984)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.3)

result = solid_1