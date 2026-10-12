import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.05097, -0.08433, 0.03934), normal=(-0.0, -0.54698, 0.83714), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.54628, -0.10641)
loop_1 = loop_1.lineTo(0.51033, -0.1261)
loop_1 = loop_1.lineTo(0.49053, -0.12958)
loop_1 = loop_1.threePointArc((0.47942, -0.12672), (0.46975, -0.12424))
loop_1 = loop_1.lineTo(0.4489, -0.10936)
loop_1 = loop_1.lineTo(0.54376, -0.10138)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_5_interval_0.stl')