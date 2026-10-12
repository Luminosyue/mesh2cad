import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.0, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
sketch_1 = sketch_1.moveTo(0.36103, -0.1485)
sketch_1 = sketch_1.circle(0.46597)
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(0.416, 0.317, 0.001), axisEnd=(0.415, 1.317, 0.001))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/greedy_greedy_test_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/greedy_greedy_test_revolve_0.stl')