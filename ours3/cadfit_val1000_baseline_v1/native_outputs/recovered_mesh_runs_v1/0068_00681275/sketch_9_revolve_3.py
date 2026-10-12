import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, 1.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.0, -4694.15008)
sketch_1 = sketch_1.circle(4694.15016)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.001, 1.001), axisEnd=(1.001, 0.001, 1.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00681275/sketch_9_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00681275/sketch_9_revolve_3.stl')