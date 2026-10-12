import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.22834, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99, -0.54448)
loop_1 = loop_1.lineTo(0.9898, -0.62497)
loop_1 = loop_1.lineTo(0.90312, -0.62482)
loop_1 = loop_1.lineTo(0.9261, -0.62229)
loop_1 = loop_1.threePointArc((0.95086, -0.60601), (0.96629, -0.59471))
loop_1 = loop_1.threePointArc((0.97351, -0.58606), (0.98029, -0.57777))
loop_1 = loop_1.lineTo(0.98847, -0.54797)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.83)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_41_interval_0.stl')