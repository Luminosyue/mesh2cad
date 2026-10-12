import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.29), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.68606, -0.86472)
loop_1 = loop_1.lineTo(-0.65114, -0.86848)
loop_1 = loop_1.lineTo(-0.5544, -0.86849)
loop_1 = loop_1.threePointArc((-0.52574, -0.86814), (-0.49671, -0.86986))
loop_1 = loop_1.threePointArc((-0.46358, -0.8707), (-0.43252, -0.86959))
loop_1 = loop_1.threePointArc((-0.38197, -0.86883), (-0.33011, -0.86891))
loop_1 = loop_1.threePointArc((-0.2778, -0.87017), (-0.2283, -0.86863))
loop_1 = loop_1.lineTo(-0.07228, -0.86845)
loop_1 = loop_1.threePointArc((-0.03038, -0.86822), (0.01249, -0.86935))
loop_1 = loop_1.lineTo(0.0936, -0.86749)
loop_1 = loop_1.threePointArc((0.18117, -0.86894), (0.26446, -0.86576))
loop_1 = loop_1.threePointArc((0.30471, -0.86724), (0.34262, -0.86742))
loop_1 = loop_1.lineTo(0.40978, -0.86472)
loop_1 = loop_1.lineTo(-0.68532, -0.86472)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_74_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_74_interval_1.stl')