import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19211, 0.5, -0.00449), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56711, 0.99551)
loop_1 = loop_1.lineTo(-0.43289, 0.99551)
loop_1 = loop_1.lineTo(-0.43289, -1.00449)
loop_1 = loop_1.lineTo(0.56711, -1.00449)
loop_1 = loop_1.lineTo(0.56711, -0.62949)
loop_1 = loop_1.lineTo(0.81711, -0.62949)
loop_1 = loop_1.lineTo(0.81711, 0.62051)
loop_1 = loop_1.lineTo(0.56711, 0.62051)
loop_1 = loop_1.lineTo(0.56711, 0.9637)
loop_1 = loop_1.lineTo(0.56711, 0.99551)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.75)

result = solid_1
