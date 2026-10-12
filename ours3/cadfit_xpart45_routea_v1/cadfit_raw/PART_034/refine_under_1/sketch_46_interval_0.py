import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.87161, -0.18485, 0.06857), normal=(-0.9914, 0.13085, -0.00282), xDir=(0.13085, 0.9914, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29895, -0.16586)
loop_1 = loop_1.lineTo(0.28617, -0.16586)
loop_1 = loop_1.lineTo(0.28253, 0.22415)
loop_1 = loop_1.lineTo(-0.3026, 0.22415)
loop_1 = loop_1.lineTo(-0.29906, -0.15482)
loop_1 = loop_1.lineTo(-0.29895, -0.16586)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_46_interval_0.stl')