import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02629, -0.13753, -0.02998), normal=(-0.00056, -0.29692, 0.9549), xDir=(-0.0, 0.9549, 0.29692))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.66954, -0.43942)
loop_1 = loop_1.lineTo(-0.60438, -0.53121)
loop_1 = loop_1.lineTo(-0.67424, -0.53121)
loop_1 = loop_1.lineTo(-0.67426, -0.43313)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_16_interval_0.stl')