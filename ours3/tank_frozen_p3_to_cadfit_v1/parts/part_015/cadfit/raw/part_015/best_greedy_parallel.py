import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.25103, 0.04727, 0.31081), normal=(4e-05, 0.00033, -1.0), xDir=(0.0, -1.0, -0.00033))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.72553, -0.20866)
loop_1 = loop_1.lineTo(-0.75115, -0.23236)
loop_1 = loop_1.lineTo(-0.76056, -0.24521)
loop_1 = loop_1.lineTo(-0.77517, -0.2335)
loop_1 = loop_1.lineTo(-0.80935, -0.20866)
loop_1 = loop_1.lineTo(-0.80898, -0.19772)
loop_1 = loop_1.threePointArc((-0.79097, -0.17728), (-0.77473, -0.15841))
loop_1 = loop_1.lineTo(-0.75041, -0.17192)
loop_1 = loop_1.lineTo(-0.72626, -0.20758)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1