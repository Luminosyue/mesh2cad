import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.98), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.41973, -0.14148)
loop_1 = loop_1.lineTo(-0.25205, -0.21172)
loop_1 = loop_1.lineTo(-0.23194, -0.21993)
loop_1 = loop_1.lineTo(-0.19557, -0.23524)
loop_1 = loop_1.lineTo(0.01731, -0.32426)
loop_1 = loop_1.threePointArc((0.10218, -0.35887), (0.18986, -0.39545))
loop_1 = loop_1.threePointArc((0.18973, -0.40206), (0.18943, -0.40787))
loop_1 = loop_1.lineTo(-0.36918, -0.18262)
loop_1 = loop_1.lineTo(-0.38783, -0.1708)
loop_1 = loop_1.lineTo(-0.39903, -0.17176)
loop_1 = loop_1.lineTo(-0.40801, -0.16086)
loop_1 = loop_1.lineTo(-0.42066, -0.1553)
loop_1 = loop_1.lineTo(-0.41973, -0.14148)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.95)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_79_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_79_interval_0.stl')