import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01333, 1.0)
loop_1 = loop_1.lineTo(-0.01333, 1.0)
loop_1 = loop_1.lineTo(-0.008, -1.0)
loop_1 = loop_1.lineTo(0.01333, -1.0)
loop_1 = loop_1.lineTo(0.01333, 0.99865)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)
plane_2 = cq.Plane(origin=(0.0, -0.01, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.03333, 1.0)
loop_1 = loop_1.lineTo(-0.02778, -1.0)
loop_1 = loop_1.lineTo(0.03333, -0.99862)
loop_1 = loop_1.lineTo(0.02778, 1.0)
loop_1 = loop_1.lineTo(-0.03194, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.02)

result = solid_1
result = result.add(solid_2)