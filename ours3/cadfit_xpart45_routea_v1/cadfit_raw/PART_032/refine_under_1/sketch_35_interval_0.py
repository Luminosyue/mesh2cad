import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.73417, 0.1548, -0.07296), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.61413, -0.13186)
loop_1 = loop_1.lineTo(-0.52818, -0.13199)
loop_1 = loop_1.lineTo(-0.52817, -0.2184)
loop_1 = loop_1.lineTo(0.61413, -0.21766)
loop_1 = loop_1.lineTo(0.61413, -0.13301)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_35_interval_0.stl')