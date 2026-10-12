import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28675, -0.24975, -0.08938), normal=(-0.0, 0.40165, 0.91579), xDir=(0.0, 0.91579, -0.40165))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31725, 0.68547)
loop_1 = loop_1.lineTo(0.31725, 0.4853)
loop_1 = loop_1.lineTo(0.33909, 0.48851)
loop_1 = loop_1.threePointArc((0.33909, 0.49389), (0.33909, 0.49905))
loop_1 = loop_1.lineTo(0.33909, 0.52868)
loop_1 = loop_1.lineTo(0.33909, 0.53905)
loop_1 = loop_1.threePointArc((0.33909, 0.54548), (0.33909, 0.55217))
loop_1 = loop_1.lineTo(0.33909, 0.57049)
loop_1 = loop_1.lineTo(0.33909, 0.6819)
loop_1 = loop_1.lineTo(0.31725, 0.68547)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_29_interval_0.stl')