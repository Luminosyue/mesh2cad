import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.54892, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.85075, 0.47257)
loop_1 = loop_1.lineTo(0.81041, 0.05941)
loop_1 = loop_1.threePointArc((0.82248, 0.07944), (0.83565, 0.09958))
loop_1 = loop_1.lineTo(0.85347, 0.15493)
loop_1 = loop_1.lineTo(0.85501, 0.21703)
loop_1 = loop_1.threePointArc((0.85508, 0.26878), (0.8544, 0.3182))
loop_1 = loop_1.threePointArc((0.85447, 0.3668), (0.85486, 0.41713))
loop_1 = loop_1.lineTo(0.85126, 0.46917)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_44_interval_0.stl')