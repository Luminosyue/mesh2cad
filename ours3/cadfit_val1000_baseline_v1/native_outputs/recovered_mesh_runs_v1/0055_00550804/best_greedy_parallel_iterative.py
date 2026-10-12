import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01003, 0.13364, 0.14675), normal=(-0.0, -1.0, 0.0), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98997, 0.6013)
loop_1 = loop_1.lineTo(0.98997, -0.30779)
loop_1 = loop_1.lineTo(-1.01003, -0.30779)
loop_1 = loop_1.lineTo(-1.00889, 0.6013)
loop_1 = loop_1.lineTo(-0.7373, 0.59883)
loop_1 = loop_1.lineTo(-0.7373, 0.01039)
loop_1 = loop_1.lineTo(0.71724, 0.01285)
loop_1 = loop_1.lineTo(0.71838, 0.6013)
loop_1 = loop_1.lineTo(0.98685, 0.6013)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.27)

result = solid_1
