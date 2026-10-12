import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01427, -1.0, 0.14803), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.58573, 0.05803)
loop_1 = loop_1.lineTo(0.61427, 0.05616)
loop_1 = loop_1.lineTo(0.61427, -0.06197)
loop_1 = loop_1.lineTo(-0.58573, -0.06055)
loop_1 = loop_1.lineTo(-0.58573, 0.05785)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.02328, 1.0, 0.1501), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.62328, 0.0601)
loop_1 = loop_1.lineTo(0.62328, -0.0599)
loop_1 = loop_1.lineTo(-0.57672, -0.0583)
loop_1 = loop_1.lineTo(-0.57672, 0.0601)
loop_1 = loop_1.lineTo(0.62293, 0.0601)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)