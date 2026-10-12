import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29066, -0.02363)
loop_1 = loop_1.threePointArc((-0.27597, -0.02102), (-0.2622, -0.01707))
loop_1 = loop_1.threePointArc((-0.2416, -0.01161), (-0.22043, -0.00662))
loop_1 = loop_1.threePointArc((-0.19611, -0.00287), (-0.17107, -0.00011))
loop_1 = loop_1.threePointArc((-0.14557, 0.00021), (-0.11946, -0.00035))
loop_1 = loop_1.threePointArc((-0.05472, -0.00317), (0.01217, -0.00809))
loop_1 = loop_1.threePointArc((0.05563, -0.01084), (0.10041, -0.01438))
loop_1 = loop_1.threePointArc((0.16545, -0.02107), (0.22761, -0.02622))
loop_1 = loop_1.lineTo(0.27917, -0.03087)
loop_1 = loop_1.threePointArc((0.29141, -0.02276), (0.29355, -0.01766))
loop_1 = loop_1.lineTo(0.28821, -0.00494)
loop_1 = loop_1.threePointArc((0.27671, 0.00217), (0.27156, 0.00265))
loop_1 = loop_1.threePointArc((0.21671, 0.00922), (0.16432, 0.01431))
loop_1 = loop_1.threePointArc((-0.02272, 0.02668), (-0.20227, 0.02961))
loop_1 = loop_1.threePointArc((-0.23576, 0.02845), (-0.26751, 0.02713))
loop_1 = loop_1.lineTo(-0.28313, 0.01838)
loop_1 = loop_1.threePointArc((-0.29055, 0.00571), (-0.2956, -0.00702))
loop_1 = loop_1.lineTo(-0.29066, -0.02363)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.99)

result = solid_1