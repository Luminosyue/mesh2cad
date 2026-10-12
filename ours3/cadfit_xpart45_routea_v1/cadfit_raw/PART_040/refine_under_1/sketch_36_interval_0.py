import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18598, -0.08044)
loop_1 = loop_1.threePointArc((0.17803, -0.07969), (0.16976, -0.07882))
loop_1 = loop_1.lineTo(0.1523, -0.06727)
loop_1 = loop_1.threePointArc((0.14369, -0.05206), (0.14044, -0.0441))
loop_1 = loop_1.lineTo(0.13869, -0.02629)
loop_1 = loop_1.threePointArc((0.14112, -0.01881), (0.14366, -0.01101))
loop_1 = loop_1.lineTo(0.16247, 0.00291)
loop_1 = loop_1.lineTo(0.19122, -0.07923)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_36_interval_0.stl')