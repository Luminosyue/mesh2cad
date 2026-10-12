import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.2164), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77075, 0.54792)
loop_1 = loop_1.threePointArc((0.77869, 0.53776), (0.78115, 0.53421))
loop_1 = loop_1.threePointArc((0.79737, 0.51107), (0.81302, 0.489))
loop_1 = loop_1.threePointArc((0.81935, 0.47906), (0.82563, 0.46861))
loop_1 = loop_1.lineTo(0.82546, 0.54792)
loop_1 = loop_1.lineTo(0.77083, 0.54792)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_40_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_40_interval_0.stl')