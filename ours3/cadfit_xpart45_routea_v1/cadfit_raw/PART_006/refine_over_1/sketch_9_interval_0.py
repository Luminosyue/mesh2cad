import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-1.00278, 0.24256, 0.02439), normal=(0.95795, -0.2869, -0.00374), xDir=(-0.2869, -0.95796, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.15625, 0.58892)
loop_1 = loop_1.lineTo(-0.13865, 0.58335)
loop_1 = loop_1.lineTo(-0.12068, 0.57646)
loop_1 = loop_1.lineTo(-0.1068, 0.5701)
loop_1 = loop_1.lineTo(-0.01809, 0.53425)
loop_1 = loop_1.lineTo(0.00672, 0.4758)
loop_1 = loop_1.lineTo(0.01082, 0.42093)
loop_1 = loop_1.lineTo(0.01048, 0.36563)
loop_1 = loop_1.lineTo(0.00581, 0.31082)
loop_1 = loop_1.lineTo(0.00662, 0.16812)
loop_1 = loop_1.lineTo(-0.00607, 0.1507)
loop_1 = loop_1.lineTo(-0.02071, 0.1334)
loop_1 = loop_1.lineTo(-0.03728, 0.11624)
loop_1 = loop_1.lineTo(-0.12448, 0.06273)
loop_1 = loop_1.lineTo(-0.15685, 0.04897)
loop_1 = loop_1.lineTo(-0.15625, 0.58662)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_9_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_9_interval_0.stl')