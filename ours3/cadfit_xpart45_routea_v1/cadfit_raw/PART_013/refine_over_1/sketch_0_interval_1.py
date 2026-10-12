import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.03622, 0.5728, 0.0709), normal=(1e-05, 0.99997, 0.00711), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4867, 0.21559)
loop_1 = loop_1.lineTo(-0.49647, 0.2541)
loop_1 = loop_1.lineTo(-0.4062, 0.2541)
loop_1 = loop_1.lineTo(-0.42871, 0.24457)
loop_1 = loop_1.lineTo(-0.45847, 0.225)
loop_1 = loop_1.lineTo(-0.48046, 0.19048)
loop_1 = loop_1.lineTo(-0.48666, 0.17528)
loop_1 = loop_1.lineTo(-0.49125, 0.12857)
loop_1 = loop_1.threePointArc((-0.49307, 0.07598), (-0.49391, 0.0302))
loop_1 = loop_1.lineTo(-0.49341, -0.01157)
loop_1 = loop_1.threePointArc((-0.49423, -0.03754), (-0.49477, -0.05829))
loop_1 = loop_1.threePointArc((-0.49447, -0.08368), (-0.4945, -0.105))
loop_1 = loop_1.lineTo(-0.49578, -0.13035)
loop_1 = loop_1.lineTo(-0.49217, 0.21559)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_0_interval_1.stl')