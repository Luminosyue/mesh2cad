import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.18368, 0.30018, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.60352, 0.40368)
loop_1 = loop_1.lineTo(-0.60352, -0.26299)
loop_1 = loop_1.lineTo(0.39648, -0.26299)
loop_1 = loop_1.lineTo(0.39648, 0.40368)
loop_1 = loop_1.lineTo(-0.59068, 0.40368)
loop_1 = loop_1.lineTo(-0.60352, 0.40368)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(-0.55018, 0.35034)
loop_2 = loop_2.lineTo(0.34315, 0.35034)
loop_2 = loop_2.lineTo(0.34315, -0.20966)
loop_2 = loop_2.lineTo(-0.55018, -0.20966)
loop_2 = loop_2.lineTo(-0.55018, 0.34315)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1