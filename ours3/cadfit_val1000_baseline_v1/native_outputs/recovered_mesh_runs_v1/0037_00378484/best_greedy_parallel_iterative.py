import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03471, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55294, 1.0)
loop_1 = loop_1.lineTo(0.55294, -0.22775)
loop_1 = loop_1.lineTo(0.54987, -0.78716)
loop_1 = loop_1.lineTo(0.19462, -1.0)
loop_1 = loop_1.lineTo(-0.55294, -0.99642)
loop_1 = loop_1.lineTo(-0.55294, 0.99997)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1