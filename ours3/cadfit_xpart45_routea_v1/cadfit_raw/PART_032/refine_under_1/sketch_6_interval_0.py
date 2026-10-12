import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03082, -0.70802, -0.11212), normal=(0.00089, 0.99996, 0.00894), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33936, 0.14329)
loop_1 = loop_1.lineTo(-0.34784, 0.13155)
loop_1 = loop_1.threePointArc((-0.34912, 0.10792), (-0.35037, 0.08467))
loop_1 = loop_1.lineTo(-0.34255, 0.0352)
loop_1 = loop_1.lineTo(-0.3371, -0.0091)
loop_1 = loop_1.lineTo(-0.33632, -0.05599)
loop_1 = loop_1.threePointArc((-0.33506, -0.07494), (-0.33434, -0.09215))
loop_1 = loop_1.lineTo(-0.33346, -0.1055)
loop_1 = loop_1.lineTo(-0.33193, -0.11721)
loop_1 = loop_1.lineTo(-0.33928, 0.14035)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_6_interval_0.stl')