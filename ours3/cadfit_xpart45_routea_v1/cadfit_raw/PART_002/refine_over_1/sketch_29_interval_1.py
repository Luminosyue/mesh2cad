import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.16232, 0.26572, 0.33419), normal=(0.26438, 0.96442, 2e-05), xDir=(0.96442, -0.26438, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.09853, 1.17103)
loop_1 = loop_1.lineTo(0.09853, 1.12122)
loop_1 = loop_1.lineTo(0.08689, 1.11978)
loop_1 = loop_1.lineTo(0.05649, 1.11737)
loop_1 = loop_1.threePointArc((0.02688, 1.11558), (0.00622, 1.11348))
loop_1 = loop_1.lineTo(-0.00561, 1.11196)
loop_1 = loop_1.lineTo(-0.01735, 1.11013)
loop_1 = loop_1.lineTo(-0.02815, 1.1089)
loop_1 = loop_1.lineTo(-0.04888, 1.10569)
loop_1 = loop_1.lineTo(-0.06461, 1.10289)
loop_1 = loop_1.lineTo(-0.04208, 1.11395)
loop_1 = loop_1.lineTo(-0.01336, 1.12555)
loop_1 = loop_1.lineTo(0.01532, 1.13618)
loop_1 = loop_1.lineTo(0.05819, 1.15486)
loop_1 = loop_1.lineTo(0.0967, 1.1703)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_29_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_29_interval_1.stl')