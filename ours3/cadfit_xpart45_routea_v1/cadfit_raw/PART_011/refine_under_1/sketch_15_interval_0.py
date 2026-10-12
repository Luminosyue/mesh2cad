import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.66487, 0.00311, -0.01485), normal=(1.0, -0.0, 0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.64075, 0.22098)
loop_1 = loop_1.lineTo(-0.62676, -0.18902)
loop_1 = loop_1.lineTo(0.7284, -0.18902)
loop_1 = loop_1.lineTo(0.70735, 0.22098)
loop_1 = loop_1.lineTo(-0.62324, 0.22098)
loop_1 = loop_1.lineTo(-0.64075, 0.22098)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_15_interval_0.stl')