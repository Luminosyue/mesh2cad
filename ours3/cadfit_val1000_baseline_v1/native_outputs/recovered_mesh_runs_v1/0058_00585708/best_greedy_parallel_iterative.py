import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31552, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08, 1.0)
loop_1 = loop_1.lineTo(0.05793, 1.0)
loop_1 = loop_1.lineTo(0.06161, -0.37931)
loop_1 = loop_1.lineTo(0.08, -0.37931)
loop_1 = loop_1.lineTo(0.08, 0.99907)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.41)
plane_2 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.08, 0.31552)
loop_1 = loop_1.lineTo(-0.07886, -0.09828)
loop_1 = loop_1.lineTo(-0.05793, -0.09799)
loop_1 = loop_1.lineTo(-0.05907, 0.31552)
loop_1 = loop_1.lineTo(-0.07971, 0.31552)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.38)

result = solid_1
result = result.add(solid_2)