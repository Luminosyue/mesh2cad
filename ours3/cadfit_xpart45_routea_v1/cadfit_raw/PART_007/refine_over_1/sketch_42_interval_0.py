import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36834, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.99, 0.61506)
loop_1 = loop_1.lineTo(0.98988, 0.56309)
loop_1 = loop_1.lineTo(0.98513, 0.57413)
loop_1 = loop_1.lineTo(0.97896, 0.58648)
loop_1 = loop_1.lineTo(0.96571, 0.59824)
loop_1 = loop_1.lineTo(0.93468, 0.61506)
loop_1 = loop_1.lineTo(0.98994, 0.61506)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.97)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_42_interval_0.stl')