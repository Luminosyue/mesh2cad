import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36398, 0.14264, -0.25673), normal=(-0.21544, 0.97652, 0.00087), xDir=(0.97652, 0.21544, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68062, -0.51953)
loop_1 = loop_1.lineTo(0.60193, -0.91055)
loop_1 = loop_1.lineTo(0.60111, -0.74235)
loop_1 = loop_1.threePointArc((0.60039, -0.7187), (0.60044, -0.69829))
loop_1 = loop_1.lineTo(0.60061, -0.68157)
loop_1 = loop_1.lineTo(0.60148, -0.65648)
loop_1 = loop_1.lineTo(0.61057, -0.6162)
loop_1 = loop_1.lineTo(0.63091, -0.59545)
loop_1 = loop_1.lineTo(0.67426, -0.54614)
loop_1 = loop_1.lineTo(0.67978, -0.52307)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_2_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_2_interval_1.stl')