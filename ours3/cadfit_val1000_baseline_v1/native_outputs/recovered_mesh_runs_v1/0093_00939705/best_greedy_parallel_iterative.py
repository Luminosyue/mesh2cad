import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.11), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77158, 1.0)
loop_1 = loop_1.lineTo(-0.76769, -0.45455)
loop_1 = loop_1.lineTo(0.68297, -0.45067)
loop_1 = loop_1.lineTo(0.67908, 1.0)
loop_1 = loop_1.lineTo(-0.76964, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.10909), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.77158, 1.0)
loop_1 = loop_1.lineTo(-0.7677, -0.45455)
loop_1 = loop_1.lineTo(0.68297, -0.45067)
loop_1 = loop_1.lineTo(0.67909, 1.0)
loop_1 = loop_1.lineTo(-0.76964, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.11)
result = solid_1
result = result.add(solid_2)
# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -0.11), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(0.68297, 1.0)
loop_1 = loop_1.lineTo(0.6798, -0.45068)
loop_1 = loop_1.lineTo(-0.7677, -0.45069)
loop_1 = loop_1.lineTo(-0.76903, 1.0)
loop_1 = loop_1.lineTo(0.67909, 0.99742)
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(0.11)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)
