import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30836, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.8562, 0.18974)
loop_1 = loop_1.lineTo(0.85579, -0.2289)
loop_1 = loop_1.threePointArc((0.85538, -0.19652), (0.85546, -0.16312))
loop_1 = loop_1.lineTo(0.84813, -0.11156)
loop_1 = loop_1.lineTo(0.8268, -0.0857)
loop_1 = loop_1.lineTo(0.8139, -0.07371)
loop_1 = loop_1.lineTo(0.78505, -0.05952)
loop_1 = loop_1.lineTo(0.77398, -0.04422)
loop_1 = loop_1.lineTo(0.76524, -0.03386)
loop_1 = loop_1.lineTo(0.75424, -0.0078)
loop_1 = loop_1.threePointArc((0.76834, 0.00745), (0.78124, 0.02225))
loop_1 = loop_1.threePointArc((0.79187, 0.03414), (0.80138, 0.04575))
loop_1 = loop_1.lineTo(0.81624, 0.07027)
loop_1 = loop_1.threePointArc((0.82351, 0.08352), (0.83144, 0.09675))
loop_1 = loop_1.threePointArc((0.84099, 0.12073), (0.84987, 0.14349))
loop_1 = loop_1.lineTo(0.85615, 0.18942)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_65_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_65_interval_1.stl')