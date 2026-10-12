import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.59155), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16901, -0.5121)
loop_1 = loop_1.lineTo(0.17012, -0.99808)
loop_1 = loop_1.lineTo(0.44937, -0.5121)
loop_1 = loop_1.lineTo(0.16946, -0.5121)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.59)
plane_2 = cq.Plane(origin=(0.28693, 0.02478, -0.59), normal=(0.0, -0.0, 1.0), xDir=(-0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.14423, -0.22517)
loop_1 = loop_1.lineTo(0.14423, -0.71307)
loop_1 = loop_1.lineTo(0.42592, -0.22517)
loop_1 = loop_1.lineTo(0.15084, -0.22517)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.59)

result = solid_1
result = result.add(solid_2)