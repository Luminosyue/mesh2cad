import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.059)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.85883, -0.04506)
sketch_1 = sketch_1.threePointArc((-0.84894, -0.04523), (-0.83945, -0.04529))
sketch_1 = sketch_1.threePointArc((-0.83055, -0.0454), (-0.82214, -0.04523))
sketch_1 = sketch_1.threePointArc((-0.81234, -0.04271), (-0.81174, -0.0424))
sketch_1 = sketch_1.threePointArc((-0.80147, -0.03091), (-0.80017, -0.0287))
sketch_1 = sketch_1.lineTo(-0.79771, -0.01798)
sketch_1 = sketch_1.lineTo(-0.79824, 0.00877)
sketch_1 = sketch_1.lineTo(-0.80444, 0.03405)
sketch_1 = sketch_1.threePointArc((-0.81452, 0.04397), (-0.81577, 0.04447))
sketch_1 = sketch_1.threePointArc((-0.82543, 0.04664), (-0.82786, 0.04668))
sketch_1 = sketch_1.threePointArc((-0.83488, 0.0469), (-0.84149, 0.04683))
sketch_1 = sketch_1.threePointArc((-0.84761, 0.04687), (-0.85384, 0.04703))
sketch_1 = sketch_1.lineTo(-0.85883, -0.04506)
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.857, 0.002, -0.057999999999999996), axisEnd=(-0.866, -0.998, -0.057999999999999996))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_8_revolve_1.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_8_revolve_1.stl')