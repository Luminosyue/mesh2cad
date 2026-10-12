import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.14347), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.58184, 0.53269)
loop_1 = loop_1.lineTo(0.59359, 0.51596)
loop_1 = loop_1.lineTo(0.6177, 0.47297)
loop_1 = loop_1.lineTo(0.63173, 0.44321)
loop_1 = loop_1.lineTo(0.63148, 0.53269)
loop_1 = loop_1.lineTo(0.58192, 0.53269)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_65_interval_0.stl')