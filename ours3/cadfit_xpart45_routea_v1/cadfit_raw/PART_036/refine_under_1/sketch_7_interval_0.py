import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2601, 0.14183, -0.09609), normal=(0.04007, -0.7737, -0.63229), xDir=(-0.99866, -0.05172, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00143, 0.09814)
loop_1 = loop_1.lineTo(-0.02877, 0.09813)
loop_1 = loop_1.lineTo(-0.13408, 0.09814)
loop_1 = loop_1.threePointArc((-0.13842, 0.08379), (-0.14197, 0.07166))
loop_1 = loop_1.lineTo(-0.14384, 0.04433)
loop_1 = loop_1.lineTo(-0.14358, 0.02884)
loop_1 = loop_1.lineTo(-0.09125, 0.02762)
loop_1 = loop_1.lineTo(0.01066, 0.02753)
loop_1 = loop_1.threePointArc((0.01024, 0.03897), (0.00962, 0.04911))
loop_1 = loop_1.threePointArc((0.00912, 0.05812), (0.00856, 0.06482))
loop_1 = loop_1.lineTo(0.00778, 0.08073)
loop_1 = loop_1.lineTo(-0.00142, 0.09813)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_7_interval_0.stl')