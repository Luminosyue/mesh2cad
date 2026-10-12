import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.24636, -0.08534, 0.35849), normal=(2e-05, -0.00018, -1.0), xDir=(0.0, -1.0, 0.00018))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.69551, -0.3451)
loop_1 = loop_1.lineTo(-0.68544, -0.32577)
loop_1 = loop_1.lineTo(-0.6588, -0.35889)
loop_1 = loop_1.lineTo(-0.62597, -0.40127)
loop_1 = loop_1.lineTo(-0.67382, -0.44317)
loop_1 = loop_1.lineTo(-0.68544, -0.44147)
loop_1 = loop_1.lineTo(-0.71926, -0.40127)
loop_1 = loop_1.lineTo(-0.719, -0.38965)
loop_1 = loop_1.lineTo(-0.69622, -0.34645)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.83)

result = solid_1