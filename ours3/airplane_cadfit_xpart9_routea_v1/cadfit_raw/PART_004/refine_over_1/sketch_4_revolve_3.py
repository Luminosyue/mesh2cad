import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.319, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.0016, -0.09403)
sketch_1 = sketch_1.lineTo(0.94, -0.09657)
sketch_1 = sketch_1.threePointArc((0.47098, 0.35128), (0.02885, -0.09514))
sketch_1 = sketch_1.threePointArc((0.01464, -0.09451), (0.00186, -0.09406))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.479, -0.102, -0.318), axisEnd=(1.4789999999999999, -0.119, -0.318))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_4_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_4_revolve_3.stl')