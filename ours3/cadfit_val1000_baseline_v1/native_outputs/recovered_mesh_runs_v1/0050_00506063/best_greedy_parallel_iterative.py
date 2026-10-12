import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.57), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0, -0.27391)
loop_1 = loop_1.circle(0.21514)
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.57)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.57), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(0.0, -0.27391)
loop_1 = loop_1.circle(0.21514)
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(1.57)
plane_3 = cq.Plane(origin=(0.0, 0.0, -0.57), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_3 = cq.Workplane(plane_3)
loop_1 = sketch_3.moveTo(0.0, -0.27391)
loop_1 = loop_1.circle(0.21514)
sketch_3=sketch_3.add(loop_1)
solid_3 = sketch_3.extrude(1.57)
plane_4 = cq.Plane(origin=(0.0, 0.0, -0.57), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_4 = cq.Workplane(plane_4)
loop_1 = sketch_4.moveTo(-0.0, -0.27391)
loop_1 = loop_1.circle(0.21514)
sketch_4=sketch_4.add(loop_1)
solid_4 = sketch_4.extrude(1.57)
result = solid_1
result = result.add(solid_2)
result = result.add(solid_3)
result = result.add(solid_4)
# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, 0.0, -1.0), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(0.0, 0.0006)
loop_1 = loop_1.circle(0.4894)
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(0.43)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)
