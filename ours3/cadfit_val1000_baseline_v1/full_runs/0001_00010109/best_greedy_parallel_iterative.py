import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.34902, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.0, 0.2209)
loop_1 = loop_1.lineTo(0.0603, 0.21789)
loop_1 = loop_1.lineTo(0.0583, -0.2209)
loop_1 = loop_1.lineTo(-1.0, -0.21789)
loop_1 = loop_1.lineTo(-1.0, 0.21989)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.53)
plane_2 = cq.Plane(origin=(0.0, 0.0, -0.2209), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_2 = cq.Workplane(plane_2)
loop_1 = sketch_2.moveTo(-0.34902, 1.0)
loop_1 = loop_1.lineTo(-0.3469, -0.0603)
loop_1 = loop_1.lineTo(0.18114, -0.05818)
loop_1 = loop_1.lineTo(0.17901, 1.0)
loop_1 = loop_1.lineTo(-0.34796, 1.0)
loop_1 = loop_1.close()
sketch_2=sketch_2.add(loop_1)
solid_2 = sketch_2.extrude(0.44)
result = solid_1
result = result.add(solid_2)
# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(-1.0, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(0.34902, 0.2209)
loop_1 = loop_1.lineTo(0.34902, -0.21789)
loop_1 = loop_1.lineTo(-0.0446, -0.2182)
loop_1 = loop_1.lineTo(0.34902, -0.2191)
loop_1 = loop_1.lineTo(-0.18114, -0.2196)
loop_1 = loop_1.lineTo(-0.18098, -0.02818)
loop_1 = loop_1.lineTo(-0.18098, -0.21789)
loop_1 = loop_1.lineTo(-0.17901, 0.2209)
loop_1 = loop_1.lineTo(0.34773, 0.2209)
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(1.06)
result_op = solid_op_1

# ===== Combine using union =====
final_result = result.add(result_op)
