import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13697, -0.34048, 0.01009), normal=(0.55682, -0.83063, 0.00124), xDir=(-0.83063, -0.55682, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01295, 0.99108)
loop_1 = loop_1.lineTo(0.02845, 0.98972)
loop_1 = loop_1.lineTo(0.02283, -0.77074)
loop_1 = loop_1.lineTo(0.02275, -0.79593)
loop_1 = loop_1.lineTo(0.02221, -0.96439)
loop_1 = loop_1.lineTo(-0.00056, -0.96425)
loop_1 = loop_1.lineTo(-0.01664, -0.96516)
loop_1 = loop_1.lineTo(-0.0283, -0.96421)
loop_1 = loop_1.lineTo(-0.0229, -0.94939)
loop_1 = loop_1.lineTo(-0.01825, -0.13602)
loop_1 = loop_1.lineTo(-0.01487, 0.52639)
loop_1 = loop_1.lineTo(-0.01177, 0.98813)
loop_1 = loop_1.lineTo(-0.02217, 0.98954)
loop_1 = loop_1.lineTo(0.01295, 0.99108)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_42_interval_0.stl')