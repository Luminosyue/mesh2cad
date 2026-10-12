import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00046, -1.0, 0.01042), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01343, 0.10027)
loop_1 = loop_1.lineTo(-0.01322, -0.08026)
loop_1 = loop_1.lineTo(0.00758, -0.08665)
loop_1 = loop_1.lineTo(0.01414, 0.1011)
loop_1 = loop_1.lineTo(-0.00637, 0.10763)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)
plane_2 = cq.Plane(origin=(0.00091, 1.0, 0.00198), normal=(0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.00786, 0.0992)
loop_1 = loop_1.lineTo(-0.0102, 0.0977)
loop_1 = loop_1.lineTo(-0.01266, -0.08928)
loop_1 = loop_1.lineTo(0.01201, -0.09377)
loop_1 = loop_1.lineTo(0.01452, 0.09254)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(2.0)

result = solid_1
result = result.add(solid_2)