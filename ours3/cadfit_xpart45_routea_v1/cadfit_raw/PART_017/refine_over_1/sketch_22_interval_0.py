import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08874, -0.06945, -0.0423), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08829, -0.76173)
loop_1 = loop_1.lineTo(0.1074, -0.76227)
loop_1 = loop_1.threePointArc((0.12823, -0.76069), (0.14604, -0.75933))
loop_1 = loop_1.lineTo(0.20569, -0.75074)
loop_1 = loop_1.threePointArc((0.23588, -0.74611), (0.26196, -0.74326))
loop_1 = loop_1.lineTo(0.27402, -0.74067)
loop_1 = loop_1.lineTo(0.0782, -0.76145)
loop_1 = loop_1.lineTo(0.06748, -0.761)
loop_1 = loop_1.threePointArc((0.02252, -0.75422), (-0.02267, -0.74644))
loop_1 = loop_1.lineTo(-0.04715, -0.74266)
loop_1 = loop_1.lineTo(-0.07593, -0.73627)
loop_1 = loop_1.lineTo(-0.09021, -0.73284)
loop_1 = loop_1.threePointArc((-0.10781, -0.72655), (-0.12599, -0.71957))
loop_1 = loop_1.threePointArc((-0.15912, -0.7049), (-0.19123, -0.68971))
loop_1 = loop_1.threePointArc((-0.21367, -0.67892), (-0.23131, -0.67067))
loop_1 = loop_1.lineTo(-0.24126, -0.76173)
loop_1 = loop_1.lineTo(0.08256, -0.76173)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_22_interval_0.stl')