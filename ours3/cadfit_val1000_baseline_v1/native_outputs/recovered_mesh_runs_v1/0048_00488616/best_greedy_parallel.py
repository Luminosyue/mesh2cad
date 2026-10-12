import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 1.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.07945, 0.24997)
sketch_1 = sketch_1.lineTo(-0.09168, 0.26214)
sketch_1 = sketch_1.lineTo(-0.07945, 0.24997)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.091, 0.251, 1.001), axisEnd=(0.616, -0.456, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0048_00488616/sketch_6_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0048_00488616/sketch_6_revolve_3.stl')