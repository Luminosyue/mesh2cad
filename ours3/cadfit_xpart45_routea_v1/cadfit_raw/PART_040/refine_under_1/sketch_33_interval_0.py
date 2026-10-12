import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23271, -0.06174)
loop_1 = loop_1.threePointArc((0.22591, -0.06713), (0.21946, -0.07241))
loop_1 = loop_1.lineTo(0.20188, -0.07848)
loop_1 = loop_1.lineTo(0.18143, 0.00931)
loop_1 = loop_1.threePointArc((0.19531, 0.0108), (0.20285, 0.01108))
loop_1 = loop_1.lineTo(0.21529, 0.00725)
loop_1 = loop_1.threePointArc((0.22471, 0.00115), (0.2288, -0.00269))
loop_1 = loop_1.lineTo(0.23271, -0.06174)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_33_interval_0.stl')