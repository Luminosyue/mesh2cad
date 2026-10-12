import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.6815, 0.11471, 0.00433), normal=(0.43219, 0.90178, -0.00027), xDir=(0.90178, -0.43219, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80757, -0.14595)
loop_1 = loop_1.threePointArc((0.80773, -0.10518), (0.80841, -0.06272))
loop_1 = loop_1.threePointArc((0.80846, -0.01458), (0.80912, 0.0288))
loop_1 = loop_1.threePointArc((0.80908, 0.05682), (0.80796, 0.08137))
loop_1 = loop_1.lineTo(0.80875, 0.10426)
loop_1 = loop_1.lineTo(0.80806, 0.13821)
loop_1 = loop_1.threePointArc((0.80846, 0.17497), (0.80967, 0.20824))
loop_1 = loop_1.lineTo(0.81085, 0.23076)
loop_1 = loop_1.lineTo(0.81032, 0.29063)
loop_1 = loop_1.lineTo(0.81053, 0.30537)
loop_1 = loop_1.threePointArc((0.8105, 0.27437), (0.81085, 0.25025))
loop_1 = loop_1.lineTo(0.81098, 0.31752)
loop_1 = loop_1.lineTo(0.81156, -0.23553)
loop_1 = loop_1.lineTo(0.80929, -0.20941)
loop_1 = loop_1.threePointArc((0.80795, -0.17564), (0.8076, -0.14694))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_34_interval_0.stl')