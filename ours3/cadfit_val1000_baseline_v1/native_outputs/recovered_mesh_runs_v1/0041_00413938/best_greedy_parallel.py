import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.3834), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66013, 0.14338)
loop_1 = loop_1.lineTo(-0.65749, -0.6204)
loop_1 = loop_1.lineTo(0.00264, -0.99848)
loop_1 = loop_1.lineTo(0.66013, -0.61583)
loop_1 = loop_1.lineTo(0.65752, 0.14489)
loop_1 = loop_1.lineTo(-0.00264, 0.52299)
loop_1 = loop_1.lineTo(-0.65883, 0.14413)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.51)
plane_2 = cq.Plane(origin=(-0.5208, 0.04806, 0.1268), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.04806, -0.13968)
loop_1 = loop_1.circle(0.61877)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.26)

result = solid_1
result = result.add(solid_2)