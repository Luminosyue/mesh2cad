import cadquery as cq
import math

# Plane definition from JSON
origin = (0.5, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.20998, -0.00082)
sketch_1 = sketch_1.threePointArc((0.20996, -0.01751), (0.20958, -0.0349))
sketch_1 = sketch_1.threePointArc((0.20892, -0.04207), (0.20796, -0.04933))
sketch_1 = sketch_1.threePointArc((0.20742, -0.05529), (0.20715, -0.06087))
sketch_1 = sketch_1.lineTo(0.20657, -0.07131)
sketch_1 = sketch_1.lineTo(0.19658, -0.1031)
sketch_1 = sketch_1.threePointArc((0.18278, -0.10957), (0.1773, -0.10968))
sketch_1 = sketch_1.lineTo(0.1547, -0.08978)
sketch_1 = sketch_1.threePointArc((0.14885, -0.08042), (0.14802, -0.07782))
sketch_1 = sketch_1.lineTo(0.14709, -0.06565)
sketch_1 = sketch_1.threePointArc((0.14722, -0.05645), (0.14761, -0.04688))
sketch_1 = sketch_1.threePointArc((0.14773, -0.03429), (0.14783, -0.03026))
sketch_1 = sketch_1.threePointArc((0.14837, -0.01352), (0.14872, -0.00545))
sketch_1 = sketch_1.lineTo(0.20998, -0.00082)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.179, 0.0, 0.501), axisEnd=(-0.821, 0.0, 0.501))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_039/sketch_2_revolve_0_ortho.stl')