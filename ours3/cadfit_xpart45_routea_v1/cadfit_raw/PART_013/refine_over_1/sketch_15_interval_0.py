import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03623, -0.81717, 0.06102), normal=(1e-05, 0.99997, 0.00711), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56282, -0.19731)
loop_1 = loop_1.lineTo(0.58714, -0.16442)
loop_1 = loop_1.lineTo(0.59353, -0.25834)
loop_1 = loop_1.lineTo(0.49914, -0.25834)
loop_1 = loop_1.threePointArc((0.5171, -0.24421), (0.52618, -0.23472))
loop_1 = loop_1.lineTo(0.54617, -0.21394)
loop_1 = loop_1.lineTo(0.56282, -0.19731)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_15_interval_0.stl')