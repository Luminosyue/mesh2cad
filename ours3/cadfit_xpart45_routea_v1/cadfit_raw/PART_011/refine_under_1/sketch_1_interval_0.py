import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.36252, -0.87315, -0.04543), normal=(-0.57745, 0.81606, 0.02444), xDir=(0.8163, 0.57763, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.39581, -0.21869)
loop_1 = loop_1.lineTo(0.4038, 0.19143)
loop_1 = loop_1.lineTo(-0.24006, 0.19143)
loop_1 = loop_1.lineTo(-0.25746, -0.21869)
loop_1 = loop_1.lineTo(0.00127, -0.21869)
loop_1 = loop_1.lineTo(0.01433, -0.21869)
loop_1 = loop_1.lineTo(0.01988, -0.20245)
loop_1 = loop_1.lineTo(0.03406, -0.20236)
loop_1 = loop_1.lineTo(0.04805, -0.21869)
loop_1 = loop_1.lineTo(0.07681, -0.21869)
loop_1 = loop_1.lineTo(0.1165, -0.21869)
loop_1 = loop_1.lineTo(0.3807, -0.21869)
loop_1 = loop_1.lineTo(0.39581, -0.21869)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_1_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_1_interval_0.stl')