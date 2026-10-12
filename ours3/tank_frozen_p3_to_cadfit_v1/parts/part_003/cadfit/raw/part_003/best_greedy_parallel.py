import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.056, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.47472, 0.0246)
loop_1 = loop_1.threePointArc((-0.27899, 0.02286), (-0.07519, 0.01673))
loop_1 = loop_1.threePointArc((0.00023, 0.01241), (0.07795, 0.00684))
loop_1 = loop_1.threePointArc((0.02759, -0.00398), (-0.02431, -0.01321))
loop_1 = loop_1.threePointArc((-0.45577, -0.02153), (-0.90437, -0.01208))
loop_1 = loop_1.lineTo(-0.97296, 0.00163)
loop_1 = loop_1.lineTo(-0.83046, 0.01676)
loop_1 = loop_1.threePointArc((-0.65626, 0.02305), (-0.47544, 0.02459))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)
plane_2 = cq.Plane(origin=(0.0, -0.95, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.02601, 0.00128)
loop_1 = loop_1.circle(0.02235)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.94)

result = solid_1
result = result.add(solid_2)