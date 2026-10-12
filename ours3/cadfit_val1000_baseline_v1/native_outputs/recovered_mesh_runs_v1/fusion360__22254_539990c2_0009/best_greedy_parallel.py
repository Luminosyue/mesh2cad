import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.0, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(0.00019, -0.00565)
sketch_1 = sketch_1.lineTo(-0.12057, -0.00565)
sketch_1 = sketch_1.lineTo(-0.12179, 0.16208)
sketch_1 = sketch_1.lineTo(-0.29708, 0.16208)
sketch_1 = sketch_1.lineTo(-0.30033, -0.82842)
sketch_1 = sketch_1.lineTo(-0.37302, -0.82842)
sketch_1 = sketch_1.lineTo(-0.37302, -0.38765)
sketch_1 = sketch_1.lineTo(-0.99916, -0.38765)
sketch_1 = sketch_1.lineTo(-0.99578, 0.82842)
sketch_1 = sketch_1.lineTo(0.00019, 0.82842)
sketch_1 = sketch_1.lineTo(0.00019, -0.00565)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.001, 0.05, 0.001), axisEnd=(0.001, 1.0499999999999998, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22254_539990c2_0009/sketch_0_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22254_539990c2_0009/sketch_0_revolve_0_ortho.stl')