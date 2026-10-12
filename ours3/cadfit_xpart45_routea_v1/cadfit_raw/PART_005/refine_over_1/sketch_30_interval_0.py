import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07489, 0.069, 0.53018), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35107, -0.94639)
loop_1 = loop_1.lineTo(-0.35091, -1.05128)
loop_1 = loop_1.lineTo(0.06069, -1.05097)
loop_1 = loop_1.lineTo(-0.02714, -1.04339)
loop_1 = loop_1.lineTo(-0.07904, -1.03714)
loop_1 = loop_1.lineTo(-0.11268, -1.03011)
loop_1 = loop_1.lineTo(-0.13442, -1.02761)
loop_1 = loop_1.lineTo(-0.16437, -1.02055)
loop_1 = loop_1.lineTo(-0.19908, -1.01065)
loop_1 = loop_1.lineTo(-0.23329, -0.99914)
loop_1 = loop_1.lineTo(-0.26692, -0.98604)
loop_1 = loop_1.lineTo(-0.32151, -0.96162)
loop_1 = loop_1.threePointArc((-0.33846, -0.95247), (-0.35098, -0.94634))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_30_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_30_interval_0.stl')