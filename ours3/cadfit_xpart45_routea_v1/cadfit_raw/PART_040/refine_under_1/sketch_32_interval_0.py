import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.27314, -0.17744)
loop_1 = loop_1.threePointArc((0.27244, -0.18546), (0.27168, -0.19381))
loop_1 = loop_1.lineTo(0.2581, -0.20972)
loop_1 = loop_1.lineTo(0.2295, -0.12805)
loop_1 = loop_1.threePointArc((0.24502, -0.1331), (0.25272, -0.13652))
loop_1 = loop_1.threePointArc((0.26541, -0.15292), (0.26949, -0.16052))
loop_1 = loop_1.threePointArc((0.27129, -0.16914), (0.27293, -0.17643))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_32_interval_0.stl')