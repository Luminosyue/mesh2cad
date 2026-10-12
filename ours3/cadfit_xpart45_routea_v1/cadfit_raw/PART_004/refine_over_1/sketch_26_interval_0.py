import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38223, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32923, 0.8)
loop_1 = loop_1.lineTo(0.26774, 0.76373)
loop_1 = loop_1.threePointArc((0.28282, 0.75798), (0.29482, 0.74752))
loop_1 = loop_1.threePointArc((0.30586, 0.73587), (0.3129, 0.72166))
loop_1 = loop_1.threePointArc((0.31586, 0.68742), (0.31652, 0.65253))
loop_1 = loop_1.threePointArc((0.32052, 0.57366), (0.32261, 0.49228))
loop_1 = loop_1.lineTo(0.32432, 0.31433)
loop_1 = loop_1.threePointArc((0.32474, 0.28698), (0.32408, 0.25933))
loop_1 = loop_1.lineTo(0.32708, 0.16107)
loop_1 = loop_1.threePointArc((0.32689, 0.11656), (0.328, 0.07461))
loop_1 = loop_1.threePointArc((0.3284, -0.00398), (0.32769, -0.08499))
loop_1 = loop_1.threePointArc((0.32781, -0.12506), (0.32906, -0.16275))
loop_1 = loop_1.threePointArc((0.3278, -0.23083), (0.32887, -0.29539))
loop_1 = loop_1.lineTo(0.32923, -0.34115)
loop_1 = loop_1.lineTo(0.32923, 0.7992)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_26_interval_0.stl')