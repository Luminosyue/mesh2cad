import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.41333, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00417, 0.99866)
loop_1 = loop_1.lineTo(0.00139, -1.0)
loop_1 = loop_1.lineTo(0.00417, 0.99866)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.83)
plane_2 = cq.Plane(origin=(-0.42, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00417, 1.0)
loop_1 = loop_1.lineTo(-0.00139, -1.0)
loop_1 = loop_1.lineTo(0.00139, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.84)

result = solid_1
result = result.add(solid_2)