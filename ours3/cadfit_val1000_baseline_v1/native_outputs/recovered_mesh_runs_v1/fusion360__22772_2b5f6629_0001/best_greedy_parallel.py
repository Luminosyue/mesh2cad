import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.0)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.54238, -0.23727)
sketch_1 = sketch_1.lineTo(-0.5399, -0.9997)
sketch_1 = sketch_1.lineTo(0.0, -0.99724)
sketch_1 = sketch_1.lineTo(0.00246, -0.47456)
sketch_1 = sketch_1.lineTo(0.54238, -0.4721)
sketch_1 = sketch_1.lineTo(0.54121, -0.23727)
sketch_1 = sketch_1.lineTo(-0.54115, -0.23727)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.076, 0.001, 0.001), axisEnd=(-1.076, 0.001, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22772_2b5f6629_0001/sketch_7_revolve_0_ortho.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1/native_outputs/recovered_mesh_runs_v1/fusion360__22772_2b5f6629_0001/sketch_7_revolve_0_ortho.stl')