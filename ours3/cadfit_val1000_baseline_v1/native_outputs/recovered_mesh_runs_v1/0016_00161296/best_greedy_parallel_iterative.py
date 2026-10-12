import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.05035), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01042, 1.0)
loop_1 = loop_1.lineTo(-0.00486, -1.0)
loop_1 = loop_1.lineTo(0.01042, -1.0)
loop_1 = loop_1.lineTo(0.00486, 1.0)
loop_1 = loop_1.lineTo(-0.00903, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)
plane_2 = cq.Plane(origin=(0.0, -0.01042, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-1.0, 0.05035)
loop_1 = loop_1.lineTo(-0.9986, -0.05035)
loop_1 = loop_1.lineTo(1.0, -0.04615)
loop_1 = loop_1.lineTo(0.9986, 0.05035)
loop_1 = loop_1.lineTo(-0.9986, 0.05035)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.02)

result = solid_1
result = result.add(solid_2)