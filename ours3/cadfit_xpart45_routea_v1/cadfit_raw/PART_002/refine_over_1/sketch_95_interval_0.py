import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.77303), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30123, -0.26)
loop_1 = loop_1.lineTo(0.35276, -0.25968)
loop_1 = loop_1.lineTo(0.3525, -0.05305)
loop_1 = loop_1.lineTo(0.35153, -0.06708)
loop_1 = loop_1.threePointArc((0.35009, -0.0767), (0.34811, -0.08646))
loop_1 = loop_1.lineTo(0.34443, -0.10449)
loop_1 = loop_1.threePointArc((0.33555, -0.13666), (0.32589, -0.16988))
loop_1 = loop_1.threePointArc((0.32379, -0.17877), (0.32204, -0.18719))
loop_1 = loop_1.lineTo(0.3096, -0.23328)
loop_1 = loop_1.lineTo(0.30418, -0.25219)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_95_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_95_interval_0.stl')