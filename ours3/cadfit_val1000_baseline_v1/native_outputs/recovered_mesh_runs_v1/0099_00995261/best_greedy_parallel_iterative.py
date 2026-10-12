import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.4), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0, -0.0)
loop_1 = loop_1.circle(0.99974)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.4)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.4), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.0, 0.0)
loop_1 = loop_1.circle(0.99974)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.4)
result = solid_1
result = result.add(solid_2)
# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -0.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(-0.0, -0.6)
loop_1 = loop_1.circle(0.39935)
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(0.4)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)
