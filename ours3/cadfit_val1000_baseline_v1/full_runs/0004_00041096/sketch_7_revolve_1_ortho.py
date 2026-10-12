import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.0, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-1.0, 0.08571)
sketch_1 = sketch_1.lineTo(-0.00033, 0.08571)
sketch_1 = sketch_1.lineTo(-1.0, -0.08426)
sketch_1 = sketch_1.lineTo(-1.0, 0.08426)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.001, 0.001), axisEnd=(0.001, 1.001, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0004_00041096/sketch_7_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/full_runs/0004_00041096/sketch_7_revolve_1_ortho.stl')