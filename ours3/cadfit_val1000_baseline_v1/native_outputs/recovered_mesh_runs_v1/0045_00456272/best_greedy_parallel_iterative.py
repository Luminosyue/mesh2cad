import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00937, -0.08667, -1e-05), normal=(-0.0, 1.0, 0.0), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.95994, 0.02499)
loop_1 = loop_1.lineTo(0.95994, -0.02501)
loop_1 = loop_1.lineTo(0.99063, -0.02501)
loop_1 = loop_1.lineTo(0.99063, 0.02499)
loop_1 = loop_1.lineTo(0.96074, 0.02499)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)
plane_2 = cq.Plane(origin=(0.00937, -0.08667, -1e-05), normal=(-0.0, 1.0, 0.0), xDir=(1.0, 0.0, -0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-1.00937, 0.02499)
loop_1 = loop_1.lineTo(-1.00937, -0.02501)
loop_1 = loop_1.lineTo(0.788, -0.02501)
loop_1 = loop_1.lineTo(0.788, 0.02499)
loop_1 = loop_1.lineTo(-0.98992, 0.02499)
loop_1 = loop_1.lineTo(-1.00937, 0.02499)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.17)

result = solid_1
result = result.add(solid_2)