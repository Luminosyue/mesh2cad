import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19667, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.33333, 0.00556)
loop_1 = loop_1.lineTo(-1.0, 0.00193)
loop_1 = loop_1.lineTo(0.33333, 0.00283)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)
plane_2 = cq.Plane(origin=(-0.26667, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(1.0, -0.00079)
loop_1 = loop_1.lineTo(-0.33333, -0.00365)
loop_1 = loop_1.lineTo(1.0, -0.0027)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.07)

result = solid_1
result = result.add(solid_2)