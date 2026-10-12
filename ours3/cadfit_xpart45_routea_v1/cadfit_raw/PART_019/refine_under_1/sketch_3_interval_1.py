import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.35163, -0.11741, -0.22882), normal=(0.83379, 0.00102, 0.55208), xDir=(0.00123, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.56688, -0.31038)
loop_1 = loop_1.lineTo(0.06962, -0.31198)
loop_1 = loop_1.lineTo(0.10865, -0.31229)
loop_1 = loop_1.lineTo(0.17155, -0.3118)
loop_1 = loop_1.threePointArc((0.23595, -0.31405), (0.29762, -0.31686))
loop_1 = loop_1.lineTo(0.3605, -0.31484)
loop_1 = loop_1.lineTo(0.41676, -0.32378)
loop_1 = loop_1.lineTo(0.47234, -0.31654)
loop_1 = loop_1.lineTo(0.48313, -0.31646)
loop_1 = loop_1.lineTo(0.53939, -0.32073)
loop_1 = loop_1.lineTo(0.56213, -0.31222)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_3_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_3_interval_1.stl')