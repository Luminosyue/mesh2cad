import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64962, 0.03386, -0.19358), normal=(-0.64503, -0.76416, 0.0), xDir=(-0.76416, 0.64503, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00725, 0.64642)
loop_1 = loop_1.lineTo(0.05255, 0.64642)
loop_1 = loop_1.lineTo(0.0524, 0.31007)
loop_1 = loop_1.lineTo(0.05089, 0.32746)
loop_1 = loop_1.lineTo(0.05012, 0.33794)
loop_1 = loop_1.lineTo(0.04783, 0.35879)
loop_1 = loop_1.lineTo(0.04285, 0.37787)
loop_1 = loop_1.lineTo(0.04001, 0.39298)
loop_1 = loop_1.lineTo(0.03571, 0.41882)
loop_1 = loop_1.lineTo(0.02806, 0.47195)
loop_1 = loop_1.threePointArc((0.0227, 0.50084), (0.01765, 0.52417))
loop_1 = loop_1.threePointArc((0.00999, 0.55884), (0.00265, 0.5886))
loop_1 = loop_1.lineTo(-0.00356, 0.61872)
loop_1 = loop_1.lineTo(-0.00684, 0.64112)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_14_interval_0.stl')