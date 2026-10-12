import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.94851, -0.33441, 0.97959), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0856, 0.04959)
loop_1 = loop_1.lineTo(0.0856, -0.04875)
loop_1 = loop_1.lineTo(0.04608, -0.0509)
loop_1 = loop_1.lineTo(0.00651, -0.05149)
loop_1 = loop_1.lineTo(-0.03546, -0.05037)
loop_1 = loop_1.lineTo(-0.06269, -0.04875)
loop_1 = loop_1.lineTo(-0.06269, 0.04959)
loop_1 = loop_1.lineTo(0.08371, 0.04959)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)
plane_2 = cq.Plane(origin=(0.0, -0.42001, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.89892, 0.98041)
loop_1 = loop_1.lineTo(0.99726, 0.97903)
loop_1 = loop_1.lineTo(0.99316, -0.98041)
loop_1 = loop_1.lineTo(0.89892, -0.97903)
loop_1 = loop_1.lineTo(0.89892, 0.97903)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.15)

result = solid_1
result = result.add(solid_2)