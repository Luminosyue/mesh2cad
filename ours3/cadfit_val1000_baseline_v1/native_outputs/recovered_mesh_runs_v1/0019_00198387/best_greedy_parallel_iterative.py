import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06279, -0.26333, 0.00549), normal=(-0.0, 1.0, -0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.93721, 0.23883)
loop_1 = loop_1.lineTo(1.06279, 0.23883)
loop_1 = loop_1.lineTo(1.06279, 0.10549)
loop_1 = loop_1.lineTo(-0.47054, 0.00549)
loop_1 = loop_1.lineTo(1.06279, -0.09451)
loop_1 = loop_1.lineTo(1.06279, -0.22784)
loop_1 = loop_1.lineTo(-0.93721, -0.22784)
loop_1 = loop_1.lineTo(-0.93721, 0.19508)
loop_1 = loop_1.lineTo(-0.93721, 0.23883)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)

result = solid_1
