import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12204, -0.19291, 0.07199), normal=(0.56482, 0.82522, -3e-05), xDir=(0.82522, -0.56482, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17468, 0.64259)
loop_1 = loop_1.lineTo(0.01936, 0.50009)
loop_1 = loop_1.threePointArc((0.03967, 0.49278), (0.05083, 0.48986))
loop_1 = loop_1.threePointArc((0.06548, 0.48491), (0.07759, 0.48131))
loop_1 = loop_1.lineTo(0.1164, 0.47094)
loop_1 = loop_1.lineTo(0.12054, 0.48778)
loop_1 = loop_1.lineTo(0.10577, 0.51566)
loop_1 = loop_1.threePointArc((0.07442, 0.54926), (0.03841, 0.57476))
loop_1 = loop_1.threePointArc((0.02548, 0.58183), (0.01544, 0.58662))
loop_1 = loop_1.lineTo(-0.0145, 0.60296)
loop_1 = loop_1.lineTo(-0.0398, 0.61784)
loop_1 = loop_1.lineTo(-0.0637, 0.6329)
loop_1 = loop_1.lineTo(-0.08269, 0.64044)
loop_1 = loop_1.lineTo(-0.09312, 0.64195)
loop_1 = loop_1.lineTo(-0.17466, 0.64259)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_2_interval_0.stl')