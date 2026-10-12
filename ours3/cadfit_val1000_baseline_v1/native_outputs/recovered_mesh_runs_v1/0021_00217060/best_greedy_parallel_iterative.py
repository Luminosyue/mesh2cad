import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83231, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.61538, 1.0)
loop_1 = loop_1.lineTo(0.61538, 0.84615)
loop_1 = loop_1.lineTo(0.46154, 0.84615)
loop_1 = loop_1.lineTo(0.45722, -1.0)
loop_1 = loop_1.lineTo(-0.61538, -0.99569)
loop_1 = loop_1.lineTo(-0.61108, 1.0)
loop_1 = loop_1.lineTo(0.61323, 1.0)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)
result = solid_1
# ===== Operation Script =====
plane_op_1 = cq.Plane(origin=(0.0, -0.62231, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_op_1 = cq.Workplane(plane_op_1)
loop_1 = sketch_op_1.moveTo(-0.98461, 1.0)
loop_1 = loop_1.lineTo(-0.83231, 0.99959)
loop_1 = loop_1.lineTo(-0.83272, 0.84615)
loop_1 = loop_1.lineTo(-0.98461, 0.84656)
loop_1 = loop_1.lineTo(-0.98461, 0.9998)
loop_1 = loop_1.close()
sketch_op_1=sketch_op_1.add(loop_1)
solid_op_1 = sketch_op_1.extrude(1.24)
result_op = solid_op_1
# ===== Combine using union =====
final_result = result.add(result_op)
