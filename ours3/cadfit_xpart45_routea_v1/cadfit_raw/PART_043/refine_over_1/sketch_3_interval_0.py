import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0325, 0.05891, 0.13635), normal=(-0.50233, -0.17213, -0.84737), xDir=(-0.32416, 0.946, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19223, 1.33369)
loop_1 = loop_1.lineTo(0.19574, 1.3441)
loop_1 = loop_1.lineTo(0.20629, 1.3426)
loop_1 = loop_1.lineTo(0.26043, 1.37785)
loop_1 = loop_1.lineTo(0.22781, 1.37607)
loop_1 = loop_1.lineTo(0.20167, 1.36735)
loop_1 = loop_1.lineTo(0.19168, 1.35384)
loop_1 = loop_1.threePointArc((0.18484, 1.34643), (0.17841, 1.33945))
loop_1 = loop_1.threePointArc((0.17825, 1.3315), (0.17812, 1.32487))
loop_1 = loop_1.lineTo(0.19223, 1.33369)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_3_interval_0.stl')