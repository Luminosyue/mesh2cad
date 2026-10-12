import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.10016, -0.14033, -0.66604), normal=(-0.0, 0.45962, -0.88811), xDir=(1.0, 0.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.06869, 0.33931)
loop_1 = loop_1.lineTo(0.27984, 0.33931)
loop_1 = loop_1.lineTo(0.27984, 0.30791)
loop_1 = loop_1.lineTo(0.26625, 0.31092)
loop_1 = loop_1.lineTo(0.25444, 0.3125)
loop_1 = loop_1.lineTo(0.22761, 0.31827)
loop_1 = loop_1.lineTo(0.20502, 0.32413)
loop_1 = loop_1.lineTo(0.18897, 0.325)
loop_1 = loop_1.lineTo(0.16282, 0.33187)
loop_1 = loop_1.lineTo(0.15033, 0.33215)
loop_1 = loop_1.lineTo(0.12197, 0.33669)
loop_1 = loop_1.lineTo(0.1117, 0.33674)
loop_1 = loop_1.lineTo(0.08216, 0.33923)
loop_1 = loop_1.lineTo(0.06869, 0.33931)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_16_interval_0.stl')