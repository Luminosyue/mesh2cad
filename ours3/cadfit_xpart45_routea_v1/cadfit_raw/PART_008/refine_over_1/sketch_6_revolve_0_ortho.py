import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.417, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.03045, 0.31349)
sketch_1 = sketch_1.lineTo(0.12362, 0.31366)
sketch_1 = sketch_1.threePointArc((0.22248, 0.31321), (0.31678, 0.31373))
sketch_1 = sketch_1.threePointArc((0.34748, 0.31356), (0.37632, 0.31432))
sketch_1 = sketch_1.threePointArc((0.45247, 0.31349), (0.52496, 0.31359))
sketch_1 = sketch_1.lineTo(0.671, 0.31373)
sketch_1 = sketch_1.threePointArc((0.72909, 0.31422), (0.78893, 0.31362))
sketch_1 = sketch_1.lineTo(0.82445, 0.30754)
sketch_1 = sketch_1.lineTo(0.8401, 0.30059)
sketch_1 = sketch_1.threePointArc((0.84953, 0.2935), (0.85825, 0.28731))
sketch_1 = sketch_1.lineTo(0.85705, 0.32792)
sketch_1 = sketch_1.lineTo(0.03045, 0.31349)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.418, 0.321, 0.418), axisEnd=(-0.582, 0.304, 0.418))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_6_revolve_0_ortho.stl')