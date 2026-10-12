import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02076, 0.1, -0.04567), normal=(-0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.97924, 0.40433)
loop_1 = loop_1.lineTo(-1.02076, 0.40433)
loop_1 = loop_1.lineTo(-1.02076, -0.09567)
loop_1 = loop_1.lineTo(-0.62076, -0.49567)
loop_1 = loop_1.lineTo(-0.12076, -0.49567)
loop_1 = loop_1.lineTo(-0.12076, -0.09567)
loop_1 = loop_1.lineTo(0.27924, -0.09567)
loop_1 = loop_1.lineTo(0.27924, -0.49567)
loop_1 = loop_1.lineTo(0.77924, -0.49567)
loop_1 = loop_1.lineTo(0.97924, -0.29567)
loop_1 = loop_1.lineTo(0.97924, 0.37345)
loop_1 = loop_1.lineTo(0.97924, 0.40433)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
