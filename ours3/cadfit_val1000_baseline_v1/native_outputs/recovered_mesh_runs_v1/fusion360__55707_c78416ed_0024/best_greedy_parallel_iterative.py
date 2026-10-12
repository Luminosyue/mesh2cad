import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.01928, 0.09941, 0.764), normal=(-0.0, 0.0, -1.0), xDir=(0.0, -1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49941, 0.98072)
loop_1 = loop_1.lineTo(0.49941, -1.01928)
loop_1 = loop_1.lineTo(0.19941, -1.01928)
loop_1 = loop_1.lineTo(0.19941, -0.41928)
loop_1 = loop_1.lineTo(-0.30059, -0.41928)
loop_1 = loop_1.lineTo(-0.30059, 0.38072)
loop_1 = loop_1.lineTo(0.19941, 0.38072)
loop_1 = loop_1.lineTo(0.19941, 0.98072)
loop_1 = loop_1.lineTo(0.46935, 0.98072)
loop_1 = loop_1.lineTo(0.49941, 0.98072)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.53)
result = solid_1

# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -0.766), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(0.08, 0.0)
loop_1 = loop_1.circle(0.15959)
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(1.02)
result_op = solid_op_1

# ===== Combine using cut =====
final_result = result.cut(result_op)
