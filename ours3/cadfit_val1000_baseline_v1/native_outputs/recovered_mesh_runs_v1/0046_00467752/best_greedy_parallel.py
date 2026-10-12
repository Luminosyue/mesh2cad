import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0625, 1.0)
loop_1 = loop_1.lineTo(-0.06109, 0.66667)
loop_1 = loop_1.lineTo(0.04167, 0.66525)
loop_1 = loop_1.lineTo(0.04571, -1.0)
loop_1 = loop_1.lineTo(0.0625, -1.0)
loop_1 = loop_1.lineTo(0.05742, 1.0)
loop_1 = loop_1.lineTo(-0.06108, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)
plane_2 = cq.Plane(origin=(-0.99667, -0.00101, -0.00053), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.00101, -0.00053)
loop_1 = loop_1.circle(0.06235)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.43)

result = solid_1
result = result.add(solid_2)