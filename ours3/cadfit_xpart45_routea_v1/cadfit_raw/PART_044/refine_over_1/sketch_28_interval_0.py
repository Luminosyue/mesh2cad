import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.62275, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12839, 0.6604)
loop_1 = loop_1.lineTo(0.12794, 0.84)
loop_1 = loop_1.lineTo(0.06272, 0.83977)
loop_1 = loop_1.lineTo(0.06329, 0.59361)
loop_1 = loop_1.threePointArc((0.06906, 0.60077), (0.0743, 0.60761))
loop_1 = loop_1.lineTo(0.08721, 0.61166)
loop_1 = loop_1.threePointArc((0.0991, 0.6117), (0.10332, 0.61077))
loop_1 = loop_1.threePointArc((0.10896, 0.60942), (0.1146, 0.60802))
loop_1 = loop_1.lineTo(0.12617, 0.59242)
loop_1 = loop_1.lineTo(0.12839, 0.57834)
loop_1 = loop_1.lineTo(0.12839, 0.66018)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_28_interval_0.stl')