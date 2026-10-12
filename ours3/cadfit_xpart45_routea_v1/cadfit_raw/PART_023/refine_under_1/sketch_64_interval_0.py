import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.35, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28694, 0.95266)
loop_1 = loop_1.lineTo(0.28631, 0.27265)
loop_1 = loop_1.lineTo(0.28671, 0.33747)
loop_1 = loop_1.threePointArc((0.28621, 0.35904), (0.28641, 0.38103))
loop_1 = loop_1.lineTo(0.2844, 0.47853)
loop_1 = loop_1.lineTo(0.28329, 0.53554)
loop_1 = loop_1.threePointArc((0.28211, 0.56406), (0.28008, 0.59093))
loop_1 = loop_1.lineTo(0.27747, 0.60705)
loop_1 = loop_1.threePointArc((0.27623, 0.61959), (0.27604, 0.63223))
loop_1 = loop_1.lineTo(0.27933, 0.65818)
loop_1 = loop_1.threePointArc((0.28014, 0.68448), (0.27962, 0.70928))
loop_1 = loop_1.lineTo(0.28133, 0.74725)
loop_1 = loop_1.lineTo(0.28335, 0.78576)
loop_1 = loop_1.threePointArc((0.28244, 0.82724), (0.28219, 0.86996))
loop_1 = loop_1.threePointArc((0.28155, 0.8873), (0.28045, 0.90346))
loop_1 = loop_1.lineTo(0.28022, 0.93097)
loop_1 = loop_1.lineTo(0.28677, 0.95222)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_64_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_64_interval_0.stl')