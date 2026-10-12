import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.68805, -0.07268, -0.42106), normal=(-0.50572, 0.1306, -0.85275), xDir=(0.25005, 0.96823, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22807, 0.25283)
loop_1 = loop_1.lineTo(0.24438, 0.32694)
loop_1 = loop_1.lineTo(0.10482, 0.33109)
loop_1 = loop_1.lineTo(0.10469, 0.28818)
loop_1 = loop_1.lineTo(0.11853, 0.28346)
loop_1 = loop_1.lineTo(0.13971, 0.27638)
loop_1 = loop_1.lineTo(0.15684, 0.27117)
loop_1 = loop_1.lineTo(0.17925, 0.2649)
loop_1 = loop_1.lineTo(0.18961, 0.26275)
loop_1 = loop_1.lineTo(0.22807, 0.25283)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_16_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_16_interval_1.stl')