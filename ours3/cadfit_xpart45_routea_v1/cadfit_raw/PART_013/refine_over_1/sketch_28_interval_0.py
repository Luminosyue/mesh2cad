import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.2029, 0.68093, 0.03541), normal=(-0.0002, -0.99988, 0.01551), xDir=(-1.0, 0.0002, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.262, 0.28422)
loop_1 = loop_1.lineTo(0.6485, 0.27648)
loop_1 = loop_1.lineTo(0.65168, 0.23534)
loop_1 = loop_1.lineTo(0.62792, 0.24597)
loop_1 = loop_1.lineTo(0.60846, 0.25406)
loop_1 = loop_1.lineTo(0.60657, 0.26427)
loop_1 = loop_1.lineTo(-0.23922, 0.26427)
loop_1 = loop_1.lineTo(-0.26175, 0.23979)
loop_1 = loop_1.lineTo(-0.2628, 0.27554)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_28_interval_0.stl')