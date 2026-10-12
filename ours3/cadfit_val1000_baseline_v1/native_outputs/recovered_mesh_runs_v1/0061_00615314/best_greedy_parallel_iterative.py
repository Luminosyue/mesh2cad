import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.66112), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.81618)
loop_1 = loop_1.lineTo(-0.9952, -0.81618)
loop_1 = loop_1.lineTo(-0.55882, -0.81375)
loop_1 = loop_1.lineTo(-0.55398, 0.28186)
loop_1 = loop_1.lineTo(1.0, 0.28672)
loop_1 = loop_1.lineTo(0.99757, 0.81618)
loop_1 = loop_1.lineTo(-0.99758, 0.81618)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.32)

result = solid_1
