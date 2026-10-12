import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35659, -0.06704, -0.13533), normal=(-0.00567, 0.87903, 0.47673), xDir=(0.99998, 0.00645, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.63308, 0.03557)
loop_1 = loop_1.lineTo(0.61343, 0.02188)
loop_1 = loop_1.lineTo(0.59606, 0.00976)
loop_1 = loop_1.lineTo(0.58248, -0.00038)
loop_1 = loop_1.lineTo(0.56165, -0.01507)
loop_1 = loop_1.lineTo(0.55085, -0.0228)
loop_1 = loop_1.threePointArc((0.5403, -0.03031), (0.52921, -0.038))
loop_1 = loop_1.lineTo(0.50837, -0.05249)
loop_1 = loop_1.threePointArc((0.4946, -0.06196), (0.48327, -0.06982))
loop_1 = loop_1.lineTo(0.49023, -0.08927)
loop_1 = loop_1.lineTo(0.65503, -0.08927)
loop_1 = loop_1.lineTo(0.65044, -0.05946)
loop_1 = loop_1.lineTo(0.64545, -0.03251)
loop_1 = loop_1.lineTo(0.64092, -0.01081)
loop_1 = loop_1.lineTo(0.63341, 0.03362)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_28_interval_0.stl')