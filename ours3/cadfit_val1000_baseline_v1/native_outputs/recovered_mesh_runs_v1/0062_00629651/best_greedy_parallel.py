import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.24162), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50867, 1.0)
loop_1 = loop_1.lineTo(-0.50581, -0.13471)
loop_1 = loop_1.lineTo(0.50867, -0.13184)
loop_1 = loop_1.lineTo(0.5058, 1.0)
loop_1 = loop_1.lineTo(-0.50724, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.48)
plane_2 = cq.Plane(origin=(0.0, -0.51, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-1.0, 0.24162)
loop_1 = loop_1.lineTo(0.13471, 0.23946)
loop_1 = loop_1.lineTo(0.13255, -0.24162)
loop_1 = loop_1.lineTo(-1.0, -0.23946)
loop_1 = loop_1.lineTo(-1.0, 0.24054)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.02)

result = solid_1
result = result.add(solid_2)