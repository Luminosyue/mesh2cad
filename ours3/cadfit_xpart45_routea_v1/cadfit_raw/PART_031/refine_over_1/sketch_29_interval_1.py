import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38128, -0.89669, -0.09586), normal=(0.00098, -1.0, -0.00032), xDir=(-1.0, -0.00098, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13369, 0.49411)
loop_1 = loop_1.lineTo(0.00946, 0.4942)
loop_1 = loop_1.lineTo(0.05473, 0.3635)
loop_1 = loop_1.threePointArc((0.05645, 0.33407), (0.05768, 0.31066))
loop_1 = loop_1.lineTo(0.05759, 0.2928)
loop_1 = loop_1.threePointArc((0.05393, 0.25159), (0.05112, 0.21863))
loop_1 = loop_1.lineTo(0.04737, 0.19321)
loop_1 = loop_1.lineTo(0.04627, 0.12016)
loop_1 = loop_1.lineTo(0.044, 0.09362)
loop_1 = loop_1.lineTo(0.01782, 0.04818)
loop_1 = loop_1.lineTo(-0.02214, 0.01713)
loop_1 = loop_1.lineTo(0.13369, 0.01736)
loop_1 = loop_1.lineTo(0.13369, 0.48868)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_29_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_29_interval_1.stl')