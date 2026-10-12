import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.83535, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.35474)
loop_1 = loop_1.lineTo(-0.34141, 0.35292)
loop_1 = loop_1.lineTo(-0.34324, -0.35474)
loop_1 = loop_1.lineTo(-1.0, -0.35292)
loop_1 = loop_1.lineTo(-1.0, 0.35383)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)
plane_2 = cq.Plane(origin=(-0.34, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.33409, 0.01183)
loop_1 = loop_1.lineTo(0.33305, -0.30703)
loop_1 = loop_1.lineTo(-0.13026, -0.30598)
loop_1 = loop_1.lineTo(-0.12922, 0.01183)
loop_1 = loop_1.lineTo(0.33357, 0.01183)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.34)

result = solid_1
result = result.add(solid_2)