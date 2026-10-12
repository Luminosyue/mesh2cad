import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.08), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03125, 1.0)
loop_1 = loop_1.lineTo(-0.02582, -1.0)
loop_1 = loop_1.lineTo(0.03125, -1.0)
loop_1 = loop_1.lineTo(0.02582, 1.0)
loop_1 = loop_1.lineTo(-0.02989, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.08167), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.03125, 1.0)
loop_1 = loop_1.lineTo(-0.02699, -1.0)
loop_1 = loop_1.lineTo(0.03125, -1.0)
loop_1 = loop_1.lineTo(0.02699, 1.0)
loop_1 = loop_1.lineTo(-0.02987, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.17)

result = solid_1
result = result.add(solid_2)