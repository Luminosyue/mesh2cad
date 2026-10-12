import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00531, 0.6, -0.03858), normal=(-0.0, -1.0, -0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15531, 0.96142)
loop_1 = loop_1.lineTo(-0.14469, 0.96142)
loop_1 = loop_1.lineTo(-0.14157, -1.03858)
loop_1 = loop_1.lineTo(0.15531, -1.03858)
loop_1 = loop_1.lineTo(0.15375, -0.63858)
loop_1 = loop_1.lineTo(0.00531, -0.63858)
loop_1 = loop_1.lineTo(0.00687, -0.33858)
loop_1 = loop_1.lineTo(0.15531, -0.33858)
loop_1 = loop_1.lineTo(0.15531, 0.95465)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.2)

result = solid_1
