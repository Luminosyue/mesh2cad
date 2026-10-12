import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.32176, -0.10302, -0.31244), normal=(-0.03591, 0.70778, 0.70552), xDir=(0.99872, 0.05067, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.1609, -0.14183)
loop_1 = loop_1.lineTo(0.19722, -0.14218)
loop_1 = loop_1.threePointArc((0.20248, -0.15026), (0.20231, -0.15488))
loop_1 = loop_1.lineTo(0.20145, -0.18045)
loop_1 = loop_1.lineTo(0.16073, -0.18194)
loop_1 = loop_1.lineTo(0.16058, -0.16695)
loop_1 = loop_1.lineTo(0.16089, -0.1426)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.36)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_26_interval_0.stl')