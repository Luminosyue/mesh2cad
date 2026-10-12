import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32176, -0.10302, -0.31244), normal=(-0.03591, 0.70778, 0.70552), xDir=(0.99872, 0.05067, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.04839, -0.14263)
loop_1 = loop_1.lineTo(0.06963, -0.14096)
loop_1 = loop_1.lineTo(0.09063, -0.14116)
loop_1 = loop_1.lineTo(0.09017, -0.1717)
loop_1 = loop_1.lineTo(0.04314, -0.18081)
loop_1 = loop_1.lineTo(0.04567, -0.17005)
loop_1 = loop_1.lineTo(0.04839, -0.14263)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_4_interval_0.stl')