import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25397, 0.06841)
loop_1 = loop_1.circle(0.0274)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.1013), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.09409, -0.25323)
loop_1 = loop_1.lineTo(-0.09224, -0.26414)
loop_1 = loop_1.lineTo(-0.076, -0.27469)
loop_1 = loop_1.lineTo(-0.06103, -0.26075)
loop_1 = loop_1.lineTo(-0.06086, -0.24992)
loop_1 = loop_1.threePointArc((-0.06767, -0.23907), (-0.07018, -0.23696))
loop_1 = loop_1.lineTo(-0.08174, -0.23612)
loop_1 = loop_1.threePointArc((-0.09156, -0.24493), (-0.09294, -0.24754))
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.19)

result = solid_1
result = result.add(solid_2)