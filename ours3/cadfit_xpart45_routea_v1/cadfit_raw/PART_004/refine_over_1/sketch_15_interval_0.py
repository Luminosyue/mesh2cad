import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38367, -0.24972, 0.04662), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.77411, 0.8464)
loop_1 = loop_1.lineTo(0.77821, 0.83326)
loop_1 = loop_1.lineTo(0.78147, 0.80555)
loop_1 = loop_1.lineTo(0.78025, 0.47281)
loop_1 = loop_1.lineTo(0.78035, 0.29813)
loop_1 = loop_1.lineTo(0.78034, 0.19332)
loop_1 = loop_1.lineTo(0.77994, 0.00756)
loop_1 = loop_1.threePointArc((0.78011, -0.0608), (0.78108, -0.1211))
loop_1 = loop_1.threePointArc((0.78024, -0.19169), (0.78034, -0.25414))
loop_1 = loop_1.lineTo(0.79019, -0.24254)
loop_1 = loop_1.lineTo(0.79751, -0.21061)
loop_1 = loop_1.threePointArc((0.79838, -0.15992), (0.79771, -0.11639))
loop_1 = loop_1.threePointArc((0.79774, 0.28779), (0.79614, 0.67068))
loop_1 = loop_1.threePointArc((0.7963, 0.74313), (0.79367, 0.80743))
loop_1 = loop_1.lineTo(0.78265, 0.83881)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_15_interval_0.stl')