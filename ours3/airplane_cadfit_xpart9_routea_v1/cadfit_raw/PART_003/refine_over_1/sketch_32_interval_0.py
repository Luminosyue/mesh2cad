import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.9103, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11038, -0.01933)
loop_1 = loop_1.lineTo(0.11116, -0.0995)
loop_1 = loop_1.threePointArc((0.12091, -0.12104), (0.13083, -0.14341))
loop_1 = loop_1.lineTo(0.14326, -0.17305)
loop_1 = loop_1.threePointArc((0.15049, -0.18985), (0.15777, -0.20729))
loop_1 = loop_1.lineTo(0.1584, -0.01933)
loop_1 = loop_1.lineTo(0.11052, -0.01933)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_32_interval_0.stl')