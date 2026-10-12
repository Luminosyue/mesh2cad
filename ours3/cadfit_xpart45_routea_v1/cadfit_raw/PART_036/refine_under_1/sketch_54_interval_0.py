import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.23678, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26592, 0.14098)
loop_1 = loop_1.lineTo(-0.26586, 0.15112)
loop_1 = loop_1.lineTo(-0.25931, 0.16129)
loop_1 = loop_1.lineTo(-0.2335, 0.17463)
loop_1 = loop_1.lineTo(-0.22566, 0.141)
loop_1 = loop_1.lineTo(-0.26591, 0.14098)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_54_interval_0.stl')