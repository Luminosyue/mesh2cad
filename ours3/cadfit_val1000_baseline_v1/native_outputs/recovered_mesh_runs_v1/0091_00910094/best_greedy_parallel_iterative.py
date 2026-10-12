import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00154, -1.0, -0.00263), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08418, 0.02594)
loop_1 = loop_1.lineTo(-0.08418, -0.0312)
loop_1 = loop_1.lineTo(-0.04132, -0.0312)
loop_1 = loop_1.lineTo(-0.03251, -0.01327)
loop_1 = loop_1.lineTo(0.03564, -0.01333)
loop_1 = loop_1.lineTo(0.04439, -0.0312)
loop_1 = loop_1.lineTo(0.08725, -0.0312)
loop_1 = loop_1.lineTo(0.08725, 0.02594)
loop_1 = loop_1.lineTo(-0.08179, 0.02594)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(2.0)

result = solid_1
