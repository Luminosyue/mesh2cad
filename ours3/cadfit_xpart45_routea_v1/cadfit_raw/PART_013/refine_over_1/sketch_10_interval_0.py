import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.74731, -0.81998, 0.07166), normal=(-1.0, 0.0, -0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.59883, 0.27708)
loop_1 = loop_1.threePointArc((0.60597, 0.27775), (0.61283, 0.27843))
loop_1 = loop_1.threePointArc((0.586, 0.2754), (0.56613, 0.27351))
loop_1 = loop_1.lineTo(0.59818, 0.277)
loop_1 = loop_1.lineTo(0.48551, 0.27486)
loop_1 = loop_1.threePointArc((0.43144, 0.27543), (0.38568, 0.27479))
loop_1 = loop_1.lineTo(0.36415, 0.27467)
loop_1 = loop_1.lineTo(0.45417, 0.274)
loop_1 = loop_1.lineTo(0.03551, 0.2653)
loop_1 = loop_1.lineTo(0.04048, 0.27706)
loop_1 = loop_1.lineTo(0.59062, 0.27706)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.48)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_10_interval_0.stl')