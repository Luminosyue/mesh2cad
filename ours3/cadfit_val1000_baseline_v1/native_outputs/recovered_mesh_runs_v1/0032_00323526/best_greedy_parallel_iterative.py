import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66667, 0.66667)
loop_1 = loop_1.lineTo(-0.66667, 0.66251)
loop_1 = loop_1.lineTo(-0.66419, -0.33209)
loop_1 = loop_1.lineTo(0.66667, 0.3375)
loop_1 = loop_1.lineTo(0.66667, 0.66528)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.66)
plane_2 = cq.Plane(origin=(-0.83, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.66667, 0.66667)
loop_1 = loop_1.lineTo(0.66542, 0.33271)
loop_1 = loop_1.lineTo(-0.66667, -0.32917)
loop_1 = loop_1.lineTo(-0.6639, 0.66667)
loop_1 = loop_1.lineTo(0.66528, 0.66667)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.66)

result = solid_1
result = result.add(solid_2)