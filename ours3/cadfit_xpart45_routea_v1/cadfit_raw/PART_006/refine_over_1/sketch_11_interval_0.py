import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.46584, -0.36134, 0.07169), normal=(-0.77344, 0.63387, 9e-05), xDir=(0.63387, 0.77344, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28314, -0.23775)
loop_1 = loop_1.lineTo(0.28289, -0.24824)
loop_1 = loop_1.threePointArc((0.27997, -0.26897), (0.2776, -0.28762))
loop_1 = loop_1.lineTo(0.27591, -0.30025)
loop_1 = loop_1.lineTo(0.27535, -0.31074)
loop_1 = loop_1.lineTo(0.27083, -0.35226)
loop_1 = loop_1.lineTo(0.27207, -0.40055)
loop_1 = loop_1.lineTo(0.2629, -0.42333)
loop_1 = loop_1.lineTo(0.24951, -0.44778)
loop_1 = loop_1.lineTo(0.2832, -0.45753)
loop_1 = loop_1.lineTo(0.28314, -0.2402)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_interval_0.stl')