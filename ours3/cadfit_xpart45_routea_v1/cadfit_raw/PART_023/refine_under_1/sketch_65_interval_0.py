import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.32, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28694, -0.28477)
loop_1 = loop_1.lineTo(0.2863, -0.78307)
loop_1 = loop_1.threePointArc((0.28532, -0.77266), (0.28341, -0.76314))
loop_1 = loop_1.lineTo(0.28042, -0.74858)
loop_1 = loop_1.threePointArc((0.28075, -0.72507), (0.28184, -0.70094))
loop_1 = loop_1.threePointArc((0.28218, -0.67681), (0.28187, -0.65397))
loop_1 = loop_1.lineTo(0.28053, -0.61518)
loop_1 = loop_1.lineTo(0.28065, -0.56686)
loop_1 = loop_1.threePointArc((0.28117, -0.55559), (0.28104, -0.54509))
loop_1 = loop_1.threePointArc((0.28162, -0.52889), (0.283, -0.51243))
loop_1 = loop_1.lineTo(0.28413, -0.45355)
loop_1 = loop_1.threePointArc((0.28439, -0.43487), (0.2855, -0.41579))
loop_1 = loop_1.lineTo(0.28519, -0.37803)
loop_1 = loop_1.threePointArc((0.28621, -0.34833), (0.28622, -0.32011))
loop_1 = loop_1.lineTo(0.28653, -0.30004)
loop_1 = loop_1.threePointArc((0.28679, -0.29226), (0.28693, -0.28511))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_65_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_65_interval_0.stl')