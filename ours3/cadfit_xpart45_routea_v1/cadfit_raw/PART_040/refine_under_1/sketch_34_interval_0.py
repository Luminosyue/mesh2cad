import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23506, -0.21927)
loop_1 = loop_1.threePointArc((0.22742, -0.2196), (0.21945, -0.21985))
loop_1 = loop_1.threePointArc((0.21029, -0.21806), (0.20281, -0.21673))
loop_1 = loop_1.lineTo(0.18526, -0.20825)
loop_1 = loop_1.threePointArc((0.17907, -0.20137), (0.17265, -0.19419))
loop_1 = loop_1.lineTo(0.16727, -0.17566)
loop_1 = loop_1.threePointArc((0.16731, -0.16813), (0.16724, -0.16089))
loop_1 = loop_1.lineTo(0.2072, -0.12741)
loop_1 = loop_1.lineTo(0.21747, -0.12675)
loop_1 = loop_1.lineTo(0.23982, -0.21812)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_34_interval_0.stl')