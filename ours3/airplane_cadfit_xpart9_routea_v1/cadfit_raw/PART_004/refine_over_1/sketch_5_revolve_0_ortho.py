import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.076, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.94, -0.05388)
sketch_1 = sketch_1.lineTo(0.94, -0.06416)
sketch_1 = sketch_1.threePointArc((0.81626, -0.0641), (0.68808, -0.06131))
sketch_1 = sketch_1.lineTo(0.59599, -0.05949)
sketch_1 = sketch_1.lineTo(0.44951, -0.05568)
sketch_1 = sketch_1.threePointArc((0.29292, -0.05247), (0.13056, -0.04723))
sketch_1 = sketch_1.threePointArc((0.11238, -0.04707), (0.09412, -0.04646))
sketch_1 = sketch_1.lineTo(0.94, -0.05388)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.472, -0.049, -0.075), axisEnd=(-0.528, -0.04, -0.075))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_5_revolve_0_ortho.stl')