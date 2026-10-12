import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0672, 0.39943, 0.02011), normal=(-0.00125, -1.0, -0.00017), xDir=(-1.0, 0.00125, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16216, -0.52957)
loop_1 = loop_1.lineTo(0.12307, -0.53819)
loop_1 = loop_1.lineTo(0.0884, -0.54355)
loop_1 = loop_1.lineTo(0.39718, -0.54281)
loop_1 = loop_1.lineTo(0.39719, -0.41277)
loop_1 = loop_1.lineTo(0.31936, -0.4686)
loop_1 = loop_1.lineTo(0.31983, -0.48795)
loop_1 = loop_1.lineTo(0.28179, -0.48795)
loop_1 = loop_1.threePointArc((0.26185, -0.49671), (0.2417, -0.50525))
loop_1 = loop_1.threePointArc((0.22044, -0.51258), (0.20309, -0.51889))
loop_1 = loop_1.lineTo(0.16444, -0.52905)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_33_interval_0.stl')