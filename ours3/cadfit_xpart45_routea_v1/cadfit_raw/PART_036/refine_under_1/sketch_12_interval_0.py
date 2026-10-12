import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00584, 0.16689, -0.17034), normal=(0.04569, -0.99792, 0.04543), xDir=(-0.99895, -0.04574, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95459, -0.11485)
loop_1 = loop_1.lineTo(-0.97736, -0.12379)
loop_1 = loop_1.lineTo(-0.98648, -0.14194)
loop_1 = loop_1.lineTo(-0.98828, -0.15918)
loop_1 = loop_1.threePointArc((-0.98799, -0.16809), (-0.98772, -0.17534))
loop_1 = loop_1.lineTo(-0.98303, -0.19901)
loop_1 = loop_1.lineTo(-0.97878, -0.21224)
loop_1 = loop_1.lineTo(-0.96781, -0.22933)
loop_1 = loop_1.threePointArc((-0.95869, -0.23014), (-0.95135, -0.23072))
loop_1 = loop_1.lineTo(-0.935, -0.21427)
loop_1 = loop_1.lineTo(-0.92352, -0.15382)
loop_1 = loop_1.threePointArc((-0.92392, -0.14704), (-0.92425, -0.14145))
loop_1 = loop_1.lineTo(-0.93465, -0.12097)
loop_1 = loop_1.lineTo(-0.95169, -0.11416)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_12_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_12_interval_0.stl')