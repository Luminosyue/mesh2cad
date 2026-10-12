import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.41487, 0.31648)
sketch_1 = sketch_1.lineTo(0.44385, 0.31685)
sketch_1 = sketch_1.lineTo(0.49194, 0.31672)
sketch_1 = sketch_1.lineTo(0.52128, 0.31613)
sketch_1 = sketch_1.lineTo(0.41487, 0.31613)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.416, 0.317, 0.001), axisEnd=(0.416, -0.683, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_revolve_2.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_5_revolve_2.stl')