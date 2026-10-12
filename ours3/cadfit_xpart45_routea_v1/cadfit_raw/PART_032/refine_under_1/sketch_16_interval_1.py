import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.24776, 0.85423, -0.05749), normal=(-0.37674, 0.92632, -9e-05), xDir=(0.92632, 0.37674, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01778, 0.14549)
loop_1 = loop_1.lineTo(-0.01782, -0.05681)
loop_1 = loop_1.lineTo(-0.01912, -0.046)
loop_1 = loop_1.lineTo(-0.02047, -0.0013)
loop_1 = loop_1.lineTo(-0.0229, 0.00871)
loop_1 = loop_1.lineTo(-0.02358, 0.04559)
loop_1 = loop_1.lineTo(-0.02696, 0.05934)
loop_1 = loop_1.lineTo(-0.0255, 0.09247)
loop_1 = loop_1.lineTo(-0.02565, 0.10501)
loop_1 = loop_1.lineTo(-0.02299, 0.13935)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_16_interval_1.stl')