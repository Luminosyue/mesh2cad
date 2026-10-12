import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49538, 0.39978, 0.03135), normal=(0.00466, -0.99999, 1e-05), xDir=(-0.99999, -0.00466, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10362, -0.80444)
loop_1 = loop_1.lineTo(0.10385, -0.93803)
loop_1 = loop_1.lineTo(0.12513, -0.93229)
loop_1 = loop_1.lineTo(0.13604, -0.92494)
loop_1 = loop_1.threePointArc((0.14548, -0.90877), (0.15072, -0.89659))
loop_1 = loop_1.lineTo(0.14783, -0.87104)
loop_1 = loop_1.lineTo(0.14239, -0.84526)
loop_1 = loop_1.lineTo(0.12503, -0.82054)
loop_1 = loop_1.lineTo(0.10482, -0.80535)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.7)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_15_interval_0.stl')