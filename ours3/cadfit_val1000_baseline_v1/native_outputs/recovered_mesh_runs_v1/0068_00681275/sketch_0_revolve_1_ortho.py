import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, -0.909, 0.0)
normal = (0.0, 1.0, 0.0)
xdir = (1.0, 0.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(5679.92165, 0.0)
sketch_1 = sketch_1.circle(5679.92173)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.001, -0.908), axisEnd=(0.001, 1.001, -0.908))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00681275/sketch_0_revolve_1_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/0068_00681275/sketch_0_revolve_1_ortho.stl')