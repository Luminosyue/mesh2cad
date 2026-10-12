import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00064, -0.74577, 0.26997), normal=(-0.0, 0.19496, -0.98081), xDir=(0.0, -0.98081, -0.19496))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0891, 0.47526)
loop_1 = loop_1.lineTo(0.08893, -0.19591)
loop_1 = loop_1.lineTo(0.10394, -0.13122)
loop_1 = loop_1.lineTo(0.10434, 0.45309)
loop_1 = loop_1.lineTo(0.09129, 0.4729)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_12_interval_0.stl')