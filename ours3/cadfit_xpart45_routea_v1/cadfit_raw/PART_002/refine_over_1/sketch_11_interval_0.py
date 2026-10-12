import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19871, 0.38168, 0.34527), normal=(-0.14906, -0.98883, 2e-05), xDir=(-0.98883, 0.14906, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.41418, 1.11529)
loop_1 = loop_1.lineTo(-0.02908, 1.11513)
loop_1 = loop_1.threePointArc((-0.05399, 1.10561), (-0.07338, 1.09827))
loop_1 = loop_1.lineTo(-0.11534, 1.08154)
loop_1 = loop_1.threePointArc((-0.13376, 1.07471), (-0.14825, 1.06937))
loop_1 = loop_1.lineTo(-0.17771, 1.06017)
loop_1 = loop_1.lineTo(-0.19127, 1.05465)
loop_1 = loop_1.lineTo(-0.22312, 1.0426)
loop_1 = loop_1.threePointArc((-0.24846, 1.03472), (-0.27045, 1.02819))
loop_1 = loop_1.lineTo(-0.21308, 1.04982)
loop_1 = loop_1.lineTo(-0.15974, 1.06664)
loop_1 = loop_1.lineTo(-0.14906, 1.06963)
loop_1 = loop_1.lineTo(-0.40936, 1.11446)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_11_interval_0.stl')