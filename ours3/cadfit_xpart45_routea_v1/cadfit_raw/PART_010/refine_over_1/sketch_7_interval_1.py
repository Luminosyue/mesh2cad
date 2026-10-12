import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72791, -0.32009, 0.5593), normal=(0.14782, 0.00235, 0.98901), xDir=(0.0, 1.0, -0.00238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56774, -0.20439)
loop_1 = loop_1.lineTo(0.54866, -0.19706)
loop_1 = loop_1.lineTo(0.5346, -0.188)
loop_1 = loop_1.lineTo(0.51007, -0.16468)
loop_1 = loop_1.lineTo(0.49816, -0.1485)
loop_1 = loop_1.threePointArc((0.49333, -0.14237), (0.48966, -0.13761))
loop_1 = loop_1.threePointArc((0.48157, -0.13001), (0.47464, -0.12338))
loop_1 = loop_1.lineTo(0.46171, -0.10894)
loop_1 = loop_1.lineTo(0.44936, -0.10532)
loop_1 = loop_1.lineTo(0.44653, -0.20426)
loop_1 = loop_1.lineTo(0.56582, -0.20439)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_7_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_7_interval_1.stl')