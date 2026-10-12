import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.49884, 0.09182, -0.00317), normal=(-0.64804, 0.76146, 0.0152), xDir=(0.76154, 0.64811, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2971, -0.05772)
loop_1 = loop_1.lineTo(0.29862, -0.06897)
loop_1 = loop_1.lineTo(0.29956, 0.24813)
loop_1 = loop_1.threePointArc((0.28122, 0.24813), (0.267, 0.24814))
loop_1 = loop_1.lineTo(0.2858, 0.02973)
loop_1 = loop_1.lineTo(0.29287, 0.10388)
loop_1 = loop_1.lineTo(0.29363, 0.12606)
loop_1 = loop_1.lineTo(0.29322, -0.05224)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_13_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_13_interval_2.stl')