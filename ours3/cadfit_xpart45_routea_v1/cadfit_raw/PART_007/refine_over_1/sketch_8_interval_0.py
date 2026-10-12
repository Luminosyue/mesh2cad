import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.60232, -0.05985, 0.33), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.93015, -0.02352)
loop_1 = loop_1.lineTo(0.93015, -0.12473)
loop_1 = loop_1.lineTo(0.92795, -0.10928)
loop_1 = loop_1.lineTo(0.92103, -0.0848)
loop_1 = loop_1.lineTo(0.91951, -0.06914)
loop_1 = loop_1.lineTo(0.90614, -0.0483)
loop_1 = loop_1.lineTo(0.87926, -0.029)
loop_1 = loop_1.lineTo(0.92869, -0.02352)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_8_interval_0.stl')