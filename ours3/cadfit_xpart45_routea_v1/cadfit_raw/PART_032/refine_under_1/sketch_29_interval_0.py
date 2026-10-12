import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03061, -0.93801, -0.11417), normal=(0.00089, 0.99996, 0.00894), xDir=(1.0, -0.00089, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.25735, -0.30086)
loop_1 = loop_1.lineTo(0.00309, -0.30087)
loop_1 = loop_1.lineTo(0.0187, -0.3373)
loop_1 = loop_1.lineTo(0.03631, -0.38418)
loop_1 = loop_1.lineTo(0.04888, -0.40431)
loop_1 = loop_1.lineTo(0.08869, -0.43123)
loop_1 = loop_1.lineTo(0.10706, -0.43367)
loop_1 = loop_1.lineTo(0.1443, -0.43237)
loop_1 = loop_1.lineTo(0.19118, -0.39986)
loop_1 = loop_1.lineTo(0.19963, -0.3891)
loop_1 = loop_1.lineTo(0.23119, -0.34021)
loop_1 = loop_1.lineTo(0.23986, -0.32868)
loop_1 = loop_1.threePointArc((0.24806, -0.3159), (0.25573, -0.30352))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.82)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_29_interval_0.stl')