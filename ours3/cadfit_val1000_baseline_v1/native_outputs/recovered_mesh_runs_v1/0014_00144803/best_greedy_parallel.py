import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80005, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.068)
loop_1 = loop_1.lineTo(-0.6001, 0.06359)
loop_1 = loop_1.lineTo(-0.59899, 0.004)
loop_1 = loop_1.lineTo(1.0, 0.00841)
loop_1 = loop_1.lineTo(1.0, 0.0669)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.6)
plane_2 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.80005, 0.068)
loop_1 = loop_1.lineTo(0.80005, 0.0636)
loop_1 = loop_1.lineTo(0.79941, 0.004)
loop_1 = loop_1.lineTo(-0.80005, 0.0084)
loop_1 = loop_1.lineTo(-0.80005, 0.06689)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.61)

result = solid_1
result = result.add(solid_2)