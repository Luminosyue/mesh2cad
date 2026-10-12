import cadquery as cq
import math

# Plane definition from JSON
origin = (0.0, 0.0, -0.059)
normal = (0.0, 0.0, 1.0)
xdir = (0.0, 1.0, 0.0)
plane_1 = cq.Plane(origin=origin, normal=normal, xDir=xdir)
sketch_1 = cq.Workplane(plane_1)

sketch_1 = sketch_1.moveTo(-0.91691, -0.0288)
sketch_1 = sketch_1.lineTo(-0.91291, -0.03932)
sketch_1 = sketch_1.lineTo(-0.89651, -0.04443)
sketch_1 = sketch_1.threePointArc((-0.88527, -0.0447), (-0.87448, -0.04477))
sketch_1 = sketch_1.threePointArc((-0.86674, -0.04489), (-0.85882, -0.04506))
sketch_1 = sketch_1.lineTo(-0.85802, 0.047)
sketch_1 = sketch_1.threePointArc((-0.86627, 0.04699), (-0.87486, 0.04721))
sketch_1 = sketch_1.threePointArc((-0.88642, 0.0473), (-0.89739, 0.04726))
sketch_1 = sketch_1.lineTo(-0.90979, 0.04419)
sketch_1 = sketch_1.lineTo(-0.91609, 0.03373)
sketch_1 = sketch_1.lineTo(-0.91649, 0.02059)
sketch_1 = sketch_1.threePointArc((-0.91652, 0.01093), (-0.91633, 0.00178))
sketch_1 = sketch_1.threePointArc((-0.91643, -0.00797), (-0.91662, -0.01798))
sketch_1 = sketch_1.threePointArc((-0.91679, -0.0235), (-0.9169, -0.02868))
sketch_1 = sketch_1.close()
result = sketch_1.revolve(angleDegrees=360.0, axisStart=(-0.857, 0.002, -0.057999999999999996), axisEnd=(-0.849, 1.0019999999999998, -0.057999999999999996))
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_8_revolve_0.stl')
print('Successfully revolved and exported to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_001/sketch_8_revolve_0.stl')