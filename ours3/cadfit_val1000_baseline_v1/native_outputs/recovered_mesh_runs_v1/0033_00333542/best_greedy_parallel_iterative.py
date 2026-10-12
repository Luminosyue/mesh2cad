import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.15009, -0.48847, -0.03483), normal=(0.0, 1.0, -0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.84991, 0.43975)
loop_1 = loop_1.lineTo(-0.84991, -0.40771)
loop_1 = loop_1.lineTo(-0.4512, -0.2658)
loop_1 = loop_1.lineTo(-0.4512, -0.50941)
loop_1 = loop_1.lineTo(0.76913, -0.50941)
loop_1 = loop_1.lineTo(0.76913, 0.16856)
loop_1 = loop_1.lineTo(1.15009, 0.30415)
loop_1 = loop_1.lineTo(1.15009, 0.43975)
loop_1 = loop_1.lineTo(-0.82025, 0.43975)
loop_1 = loop_1.lineTo(-0.84991, 0.43975)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.49795, -0.23822)
loop_2 = loop_2.circle(0.10043)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.98)

result = solid_1
