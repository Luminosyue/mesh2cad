import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.68583, 0.11897, -0.07256), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.62363, 0.18744)
loop_1 = loop_1.lineTo(0.6022, 0.18744)
loop_1 = loop_1.lineTo(0.60206, -0.17256)
loop_1 = loop_1.lineTo(-0.62401, -0.17256)
loop_1 = loop_1.lineTo(-0.62365, 0.17186)
loop_1 = loop_1.lineTo(-0.62363, 0.18744)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_36_interval_0.stl')