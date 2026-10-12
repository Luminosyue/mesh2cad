import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.55459, 0.17247, 0.02584), normal=(0.99084, 0.13501, -0.00221), xDir=(0.13501, -0.99084, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28437, 0.26856)
loop_1 = loop_1.lineTo(0.27467, -0.14261)
loop_1 = loop_1.lineTo(0.27845, -0.13118)
loop_1 = loop_1.lineTo(0.27855, -0.16149)
loop_1 = loop_1.lineTo(0.27921, -0.17411)
loop_1 = loop_1.lineTo(0.27987, -0.1877)
loop_1 = loop_1.lineTo(0.2755, -0.19947)
loop_1 = loop_1.lineTo(0.28077, -0.21058)
loop_1 = loop_1.lineTo(0.28439, 0.26296)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_1_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_1_interval_1.stl')