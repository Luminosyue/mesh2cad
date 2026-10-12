import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -1.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35294, 0.01471)
loop_1 = loop_1.lineTo(-0.35245, -0.01471)
loop_1 = loop_1.lineTo(0.35294, -0.01274)
loop_1 = loop_1.lineTo(0.35245, 0.01471)
loop_1 = loop_1.lineTo(-0.35245, 0.01471)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
