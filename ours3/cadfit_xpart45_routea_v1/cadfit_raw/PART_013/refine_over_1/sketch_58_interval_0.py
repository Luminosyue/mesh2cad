import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.21188), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.91587, 0.24585)
loop_1 = loop_1.lineTo(0.90166, 0.25378)
loop_1 = loop_1.lineTo(0.87623, 0.25948)
loop_1 = loop_1.threePointArc((0.89502, 0.25017), (0.91425, 0.24025))
loop_1 = loop_1.threePointArc((0.92132, 0.21597), (0.92539, 0.19683))
loop_1 = loop_1.threePointArc((0.9289, 0.16537), (0.93075, 0.14304))
loop_1 = loop_1.lineTo(0.75242, 0.27947)
loop_1 = loop_1.lineTo(0.78351, 0.27446)
loop_1 = loop_1.lineTo(0.811, 0.27119)
loop_1 = loop_1.lineTo(0.83887, 0.269)
loop_1 = loop_1.lineTo(0.86421, 0.26771)
loop_1 = loop_1.threePointArc((0.88836, 0.25975), (0.91259, 0.24955))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_58_interval_0.stl')