import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01686, -0.14209, 0.16591), normal=(0.0, 1.0, 0.0), xDir=(1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.01686, 0.69069)
loop_1 = loop_1.lineTo(-0.26176, 0.00847)
loop_1 = loop_1.lineTo(-0.07651, 0.55317)
loop_1 = loop_1.lineTo(0.17738, 0.00847)
loop_1 = loop_1.lineTo(0.46942, 0.00847)
loop_1 = loop_1.lineTo(0.98038, 0.6494)
loop_1 = loop_1.lineTo(0.53999, -0.35888)
loop_1 = loop_1.lineTo(-0.42503, -0.35888)
loop_1 = loop_1.lineTo(-1.01408, 0.68575)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1