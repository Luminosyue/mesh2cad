import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.95648, -0.43264, -0.01892), normal=(0.92513, 0.37964, -0.00066), xDir=(0.37964, -0.92513, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05532, -0.08338)
loop_1 = loop_1.lineTo(0.05546, -0.59151)
loop_1 = loop_1.threePointArc((0.03193, -0.58554), (0.01325, -0.57993))
loop_1 = loop_1.lineTo(-0.01985, -0.57194)
loop_1 = loop_1.threePointArc((-0.0467, -0.55546), (-0.06976, -0.54102))
loop_1 = loop_1.lineTo(-0.08526, -0.41576)
loop_1 = loop_1.lineTo(-0.09162, -0.28781)
loop_1 = loop_1.lineTo(-0.089, -0.16498)
loop_1 = loop_1.lineTo(-0.06784, -0.12469)
loop_1 = loop_1.lineTo(-0.01451, -0.0993)
loop_1 = loop_1.threePointArc((0.02025, -0.09141), (0.04905, -0.08481))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_15_interval_0.stl')