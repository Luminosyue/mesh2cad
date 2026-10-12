import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.80736, -0.6183, 0.03639), normal=(-0.92514, 0.3787, 0.02655), xDir=(0.37883, 0.92546, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.42782, 0.12342)
loop_1 = loop_1.lineTo(1.42195, 0.16136)
loop_1 = loop_1.lineTo(1.3835, 0.07463)
loop_1 = loop_1.lineTo(1.35251, 0.05909)
loop_1 = loop_1.threePointArc((1.34522, 0.05676), (1.33823, 0.05452))
loop_1 = loop_1.lineTo(1.42391, 0.05452)
loop_1 = loop_1.threePointArc((1.42354, 0.08797), (1.42319, 0.11819))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_11_interval_1.stl')