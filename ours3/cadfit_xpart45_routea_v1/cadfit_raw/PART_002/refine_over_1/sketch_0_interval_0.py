import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03231, 0.38769, 0.16335), normal=(0.00036, -0.99292, -0.11878), xDir=(-1.0, -0.00036, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22744, 0.2199)
loop_1 = loop_1.lineTo(-0.22743, 0.12813)
loop_1 = loop_1.lineTo(-0.21815, 0.13972)
loop_1 = loop_1.lineTo(-0.20385, 0.1622)
loop_1 = loop_1.lineTo(-0.20812, 0.17238)
loop_1 = loop_1.lineTo(-0.2103, 0.19947)
loop_1 = loop_1.lineTo(-0.21888, 0.21207)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_0_interval_0.stl')