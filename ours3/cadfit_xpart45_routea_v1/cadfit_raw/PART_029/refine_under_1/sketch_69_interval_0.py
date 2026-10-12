import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.00908), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01411, 0.44125)
loop_1 = loop_1.threePointArc((-0.01035, 0.4238), (-0.00687, 0.40554))
loop_1 = loop_1.lineTo(-0.00337, 0.3842)
loop_1 = loop_1.lineTo(-0.003, 0.3695)
loop_1 = loop_1.lineTo(-0.00379, 0.35365)
loop_1 = loop_1.lineTo(-0.00606, 0.33599)
loop_1 = loop_1.lineTo(-0.00737, 0.3192)
loop_1 = loop_1.lineTo(-0.00784, 0.30227)
loop_1 = loop_1.lineTo(-0.00774, 0.28996)
loop_1 = loop_1.lineTo(-0.01199, 0.2717)
loop_1 = loop_1.lineTo(-0.01917, 0.44868)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_69_interval_0.stl')