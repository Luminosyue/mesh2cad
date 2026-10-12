import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.417, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.85664, 0.34222)
sketch_1 = sketch_1.lineTo(-0.02439, 0.31372)
sketch_1 = sketch_1.threePointArc((0.42575, 0.31403), (0.85707, 0.32709))
sketch_1 = sketch_1.lineTo(0.85665, 0.34159)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.418, 0.321, 0.418), axisEnd=(1.418, 0.336, 0.418))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_3.stl')