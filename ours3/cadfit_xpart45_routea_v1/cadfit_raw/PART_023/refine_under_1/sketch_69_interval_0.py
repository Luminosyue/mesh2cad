import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.18312, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49861, 0.94661)
loop_1 = loop_1.lineTo(0.5028, 0.64697)
loop_1 = loop_1.threePointArc((0.48619, 0.64814), (0.47489, 0.64939))
loop_1 = loop_1.lineTo(0.46047, 0.65442)
loop_1 = loop_1.lineTo(0.47053, 0.66817)
loop_1 = loop_1.lineTo(0.47037, 0.7029)
loop_1 = loop_1.lineTo(0.46603, 0.73573)
loop_1 = loop_1.lineTo(0.4618, 0.79591)
loop_1 = loop_1.lineTo(0.46155, 0.85318)
loop_1 = loop_1.lineTo(0.47092, 0.88637)
loop_1 = loop_1.lineTo(0.47072, 0.93423)
loop_1 = loop_1.threePointArc((0.48582, 0.94544), (0.49838, 0.94657))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_69_interval_0.stl')