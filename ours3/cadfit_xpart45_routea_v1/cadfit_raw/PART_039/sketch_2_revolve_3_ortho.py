import cadquery as cq
import math

# Plane definition from JSON
origin = (0.5, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.20715, 0.07296)
sketch_1 = sketch_1.threePointArc((0.20718, 0.06679), (0.20744, 0.06086))
sketch_1 = sketch_1.lineTo(0.20916, 0.04224)
sketch_1 = sketch_1.threePointArc((0.20972, 0.02121), (0.20994, 0.00835))
sketch_1 = sketch_1.lineTo(0.14882, 0.00453)
sketch_1 = sketch_1.lineTo(0.14811, 0.0316)
sketch_1 = sketch_1.lineTo(0.14857, 0.05299)
sketch_1 = sketch_1.lineTo(0.14895, 0.07352)
sketch_1 = sketch_1.threePointArc((0.15223, 0.08338), (0.15313, 0.08604))
sketch_1 = sketch_1.threePointArc((0.16139, 0.09894), (0.16354, 0.10403))
sketch_1 = sketch_1.lineTo(0.20715, 0.07296)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.179, 0.0, 0.501), axisEnd=(1.1789999999999998, -0.006, 0.501))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_revolve_3_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_revolve_3_ortho.stl')