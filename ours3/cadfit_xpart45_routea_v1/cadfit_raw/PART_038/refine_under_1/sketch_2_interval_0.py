import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19271, -0.19241, -0.00947), normal=(-0.00891, -0.99996, -0.00155), xDir=(-0.99996, 0.00891, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.80019, 0.02582)
loop_1 = loop_1.lineTo(0.79919, 0.06178)
loop_1 = loop_1.lineTo(0.79833, 0.07987)
loop_1 = loop_1.threePointArc((0.79754, 0.08831), (0.79534, 0.09457))
loop_1 = loop_1.lineTo(-0.67945, 0.09303)
loop_1 = loop_1.lineTo(-0.68957, 0.09301)
loop_1 = loop_1.lineTo(-0.71393, 0.09404)
loop_1 = loop_1.lineTo(-0.78223, 0.09453)
loop_1 = loop_1.threePointArc((-0.7916, 0.09026), (-0.79322, 0.0842))
loop_1 = loop_1.threePointArc((-0.79708, 0.06546), (-0.79462, 0.05063))
loop_1 = loop_1.threePointArc((-0.79829, 0.0408), (-0.79792, 0.03437))
loop_1 = loop_1.lineTo(-0.67675, 0.02563)
loop_1 = loop_1.lineTo(0.71665, 0.02557)
loop_1 = loop_1.threePointArc((0.72471, 0.02662), (0.72683, 0.02644))
loop_1 = loop_1.threePointArc((0.73495, 0.02675), (0.73762, 0.02361))
loop_1 = loop_1.threePointArc((0.74871, 0.02652), (0.7571, 0.0263))
loop_1 = loop_1.lineTo(0.80007, 0.02593)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_2_interval_0.stl')