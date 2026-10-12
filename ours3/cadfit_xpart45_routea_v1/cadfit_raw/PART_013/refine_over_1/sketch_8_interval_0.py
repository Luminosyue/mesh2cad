import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1999, 0.12325, 0.30083), normal=(0.00024, 0.01364, -0.99991), xDir=(0.0, -0.99991, -0.01364))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96862, 0.7327)
loop_1 = loop_1.lineTo(0.96865, 0.64278)
loop_1 = loop_1.lineTo(0.96244, 0.6632)
loop_1 = loop_1.lineTo(0.94401, 0.68756)
loop_1 = loop_1.lineTo(0.92313, 0.70316)
loop_1 = loop_1.lineTo(0.91976, 0.7153)
loop_1 = loop_1.lineTo(0.90465, 0.7327)
loop_1 = loop_1.lineTo(0.96762, 0.7327)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_8_interval_0.stl')