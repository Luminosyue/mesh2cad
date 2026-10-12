import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.06113, 0.01419, 1.0), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.01419, -0.06113)
loop_1 = loop_1.lineTo(0.93807, -0.44381)
loop_1 = loop_1.lineTo(0.7213, -0.76824)
loop_1 = loop_1.lineTo(0.39688, -0.98501)
loop_1 = loop_1.lineTo(0.01419, -1.06113)
loop_1 = loop_1.lineTo(-0.36849, -0.98501)
loop_1 = loop_1.lineTo(-0.69291, -0.76824)
loop_1 = loop_1.lineTo(-0.90969, -0.44381)
loop_1 = loop_1.lineTo(-0.98581, -0.06113)
loop_1 = loop_1.lineTo(-0.90969, 0.32155)
loop_1 = loop_1.lineTo(-0.69291, 0.64598)
loop_1 = loop_1.lineTo(-0.36849, 0.86275)
loop_1 = loop_1.lineTo(0.01419, 0.93887)
loop_1 = loop_1.lineTo(0.39688, 0.86275)
loop_1 = loop_1.lineTo(0.7213, 0.64598)
loop_1 = loop_1.lineTo(0.93807, 0.32155)
loop_1 = loop_1.lineTo(1.01229, -0.05156)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.01419, -0.06113)
loop_2 = loop_2.circle(0.12349)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
