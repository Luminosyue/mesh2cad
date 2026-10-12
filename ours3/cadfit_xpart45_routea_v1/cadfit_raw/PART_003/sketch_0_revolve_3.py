import cadquery as cq
import math

# Plane definition from JSON
origin = (-0.038, 0.0, 0.0)
normal = (1.0, 0.0, 0.0)
xdir = (0.0, -1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.63144, 0.02104)
sketch_1 = sketch_1.threePointArc((-0.53241, 0.02068), (-0.42926, 0.01923))
sketch_1 = sketch_1.threePointArc((-0.35257, 0.01654), (-0.27333, 0.01281))
sketch_1 = sketch_1.lineTo(-0.21375, 0.01041)
sketch_1 = sketch_1.lineTo(-0.15782, 0.00743)
sketch_1 = sketch_1.lineTo(-0.14273, 0.00176)
sketch_1 = sketch_1.threePointArc((-0.57292, 0.06535), (-0.99393, -0.00101))
sketch_1 = sketch_1.lineTo(-0.98544, 0.01269)
sketch_1 = sketch_1.lineTo(-0.97297, 0.01584)
sketch_1 = sketch_1.threePointArc((-0.95346, 0.01675), (-0.93373, 0.01683))
sketch_1 = sketch_1.lineTo(-0.81508, 0.02017)
sketch_1 = sketch_1.threePointArc((-0.72511, 0.02089), (-0.63199, 0.02098))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.561, 0.0, -0.037), axisEnd=(0.439, 0.001, -0.037))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_0_revolve_3.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_003/sketch_0_revolve_3.stl')