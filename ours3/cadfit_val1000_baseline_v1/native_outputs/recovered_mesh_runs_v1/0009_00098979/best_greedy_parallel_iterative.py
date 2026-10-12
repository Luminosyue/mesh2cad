import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69435, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.82609, 0.00348)
loop_1 = loop_1.lineTo(-0.82656, -0.17739)
loop_1 = loop_1.lineTo(-1.0, -0.17692)
loop_1 = loop_1.lineTo(-0.99953, 0.00348)
loop_1 = loop_1.lineTo(-0.82632, 0.00348)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.39)
plane_2 = cq.Plane(origin=(-0.69435, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(1.0, 0.17739)
loop_1 = loop_1.lineTo(0.99896, 0.00348)
loop_1 = loop_1.lineTo(-0.3913, 0.0066)
loop_1 = loop_1.lineTo(-0.39026, 0.17739)
loop_1 = loop_1.lineTo(0.99896, 0.17739)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.39)

result = solid_1
result = result.add(solid_2)