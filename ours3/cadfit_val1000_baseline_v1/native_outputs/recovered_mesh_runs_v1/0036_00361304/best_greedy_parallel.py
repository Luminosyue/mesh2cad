import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.16667, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.0, 0.04167)
loop_1 = loop_1.lineTo(0.50228, -0.45833)
loop_1 = loop_1.lineTo(1.0, -0.4572)
loop_1 = loop_1.lineTo(1.0, 0.0411)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)
plane_2 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.66667, 0.45833)
loop_1 = loop_1.lineTo(-0.16667, 0.45611)
loop_1 = loop_1.lineTo(-0.16444, -0.375)
loop_1 = loop_1.lineTo(0.66667, -0.37278)
loop_1 = loop_1.lineTo(0.66667, 0.45722)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.33)

result = solid_1
result = result.add(solid_2)