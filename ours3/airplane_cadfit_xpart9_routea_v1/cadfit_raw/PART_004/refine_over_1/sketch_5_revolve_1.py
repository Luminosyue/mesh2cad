import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.076, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.00734, -0.04356)
sketch_1 = sketch_1.lineTo(0.94, -0.04608)
sketch_1 = sketch_1.threePointArc((0.50366, 0.37236), (0.09408, -0.04649))
sketch_1 = sketch_1.lineTo(-0.00656, -0.04358)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.472, -0.049, -0.075), axisEnd=(1.472, -0.057999999999999996, -0.075))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_revolve_1.stl')