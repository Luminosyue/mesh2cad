import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35615, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21646, 0.77063)
loop_1 = loop_1.lineTo(0.31214, 0.8)
loop_1 = loop_1.lineTo(0.12091, 0.79953)
loop_1 = loop_1.lineTo(0.13708, 0.78771)
loop_1 = loop_1.lineTo(0.15156, 0.77742)
loop_1 = loop_1.lineTo(0.17242, 0.77475)
loop_1 = loop_1.lineTo(0.18665, 0.77115)
loop_1 = loop_1.lineTo(0.20925, 0.77092)
loop_1 = loop_1.lineTo(0.22252, 0.77022)
loop_1 = loop_1.threePointArc((0.23359, 0.76888), (0.24495, 0.76736))
loop_1 = loop_1.lineTo(0.21662, 0.77063)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_21_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_21_interval_0.stl')