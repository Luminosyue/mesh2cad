import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05972, -0.50091, 0.75526), normal=(0.0, -0.9056, 0.42414), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.38835, 1.09171)
loop_1 = loop_1.threePointArc((0.35179, 1.09206), (0.3167, 1.0915))
loop_1 = loop_1.threePointArc((0.23321, 1.09249), (0.16004, 1.09205))
loop_1 = loop_1.lineTo(-0.02466, 1.09224)
loop_1 = loop_1.lineTo(-0.13874, 1.09308)
loop_1 = loop_1.threePointArc((-0.18389, 1.09293), (-0.22359, 1.09371))
loop_1 = loop_1.lineTo(0.57468, 1.09332)
loop_1 = loop_1.threePointArc((0.52674, 1.09201), (0.48073, 1.09142))
loop_1 = loop_1.lineTo(0.44505, 1.09179)
loop_1 = loop_1.threePointArc((0.41714, 1.09144), (0.39524, 1.09162))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_20_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_20_interval_1.stl')