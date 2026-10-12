import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.29211, -0.03743, 0.72352), normal=(0.38651, -0.0014, 0.92228), xDir=(-0.0, 1.0, 0.00152))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.75762, 0.30929)
loop_1 = loop_1.lineTo(0.75724, -0.33845)
loop_1 = loop_1.lineTo(-0.69276, -0.33713)
loop_1 = loop_1.lineTo(-0.69238, 0.31063)
loop_1 = loop_1.lineTo(0.73651, 0.30931)
loop_1 = loop_1.lineTo(0.75762, 0.30929)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_9_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_9_interval_1.stl')