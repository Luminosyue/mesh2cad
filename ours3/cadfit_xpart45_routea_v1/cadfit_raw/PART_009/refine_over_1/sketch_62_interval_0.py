import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.535, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.66207, -0.52758)
loop_1 = loop_1.lineTo(0.60624, -0.52979)
loop_1 = loop_1.lineTo(0.13199, -0.52863)
loop_1 = loop_1.lineTo(0.34379, -0.37874)
loop_1 = loop_1.lineTo(0.36081, -0.38317)
loop_1 = loop_1.threePointArc((0.38183, -0.3944), (0.40185, -0.40466))
loop_1 = loop_1.lineTo(0.41298, -0.40968)
loop_1 = loop_1.threePointArc((0.43964, -0.41598), (0.46497, -0.42147))
loop_1 = loop_1.threePointArc((0.49174, -0.41978), (0.51697, -0.41782))
loop_1 = loop_1.threePointArc((0.54324, -0.4097), (0.568, -0.40183))
loop_1 = loop_1.lineTo(0.60122, -0.41908)
loop_1 = loop_1.lineTo(0.62019, -0.45071)
loop_1 = loop_1.lineTo(0.62687, -0.47148)
loop_1 = loop_1.threePointArc((0.64298, -0.49859), (0.65877, -0.52398))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_62_interval_0.stl')