import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0156, -0.50363, 0.00203), normal=(-0.0, 1.0, 0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33472, 0.95448)
loop_1 = loop_1.lineTo(-0.9844, 0.17486)
loop_1 = loop_1.lineTo(-0.63407, -0.77758)
loop_1 = loop_1.lineTo(0.36593, -0.95041)
loop_1 = loop_1.lineTo(1.0156, -0.1708)
loop_1 = loop_1.lineTo(0.66528, 0.78164)
loop_1 = loop_1.lineTo(-0.31004, 0.95021)
loop_1 = loop_1.lineTo(-0.33472, 0.95448)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.0156, 0.00203)
loop_2 = loop_2.circle(0.47661)
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(1.01)

result = solid_1
