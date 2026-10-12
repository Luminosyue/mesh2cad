import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38616, -0.04642, -0.23637), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29942, -0.12422)
loop_1 = loop_1.threePointArc((-0.29928, -0.13264), (-0.29896, -0.14072))
loop_1 = loop_1.lineTo(-0.28787, -0.15705)
loop_1 = loop_1.lineTo(-0.2673, -0.16488)
loop_1 = loop_1.lineTo(-0.28497, -0.15876)
loop_1 = loop_1.lineTo(-0.25525, -0.07383)
loop_1 = loop_1.lineTo(-0.2875, -0.09103)
loop_1 = loop_1.threePointArc((-0.29155, -0.098), (-0.29586, -0.1052))
loop_1 = loop_1.lineTo(-0.29942, -0.12422)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_14_interval_0.stl')