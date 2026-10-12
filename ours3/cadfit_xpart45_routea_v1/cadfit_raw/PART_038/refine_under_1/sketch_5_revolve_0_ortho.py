import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.93722, -0.11976)
sketch_1 = sketch_1.lineTo(0.92408, -0.12103)
sketch_1 = sketch_1.threePointArc((0.90823, -0.12041), (0.89175, -0.11909))
sketch_1 = sketch_1.threePointArc((0.88318, -0.11856), (0.87444, -0.11771))
sketch_1 = sketch_1.threePointArc((0.8691, -0.1174), (0.86411, -0.11718))
sketch_1 = sketch_1.lineTo(0.83328, -0.11628)
sketch_1 = sketch_1.lineTo(0.8219, -0.11651)
sketch_1 = sketch_1.lineTo(0.79322, -0.11794)
sketch_1 = sketch_1.lineTo(0.77469, -0.11801)
sketch_1 = sketch_1.lineTo(0.76468, -0.11721)
sketch_1 = sketch_1.lineTo(0.74357, -0.11025)
sketch_1 = sketch_1.lineTo(0.93722, -0.11976)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.847, -0.11, 0.001), axisEnd=(-0.153, -0.10099999999999999, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_5_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_038/refine_under_1/sketch_5_revolve_0_ortho.stl')