import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.69956, -0.04181, 0.411), normal=(0.86333, -0.00027, 0.50464), xDir=(-0.00031, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.68631, -0.18969)
loop_1 = loop_1.lineTo(-0.76369, -0.18856)
loop_1 = loop_1.lineTo(-0.76375, 0.17868)
loop_1 = loop_1.lineTo(0.68625, 0.18645)
loop_1 = loop_1.lineTo(0.68631, -0.17114)
loop_1 = loop_1.lineTo(0.68631, -0.18969)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_29_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_29_interval_1.stl')