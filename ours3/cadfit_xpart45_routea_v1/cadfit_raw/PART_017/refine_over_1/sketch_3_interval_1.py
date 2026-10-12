import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06616, -0.43057, 0.01997), normal=(-0.00125, -1.0, -0.00017), xDir=(-1.0, 0.00125, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31282, -0.41596)
loop_1 = loop_1.lineTo(-0.29922, -0.42808)
loop_1 = loop_1.lineTo(-0.26646, -0.45366)
loop_1 = loop_1.lineTo(-0.23835, -0.4708)
loop_1 = loop_1.threePointArc((-0.21748, -0.48223), (-0.19953, -0.49232))
loop_1 = loop_1.lineTo(-0.18331, -0.50089)
loop_1 = loop_1.lineTo(-0.16307, -0.5107)
loop_1 = loop_1.lineTo(-0.14467, -0.51741)
loop_1 = loop_1.lineTo(-0.10603, -0.52887)
loop_1 = loop_1.threePointArc((-0.08701, -0.53216), (-0.0714, -0.53495))
loop_1 = loop_1.lineTo(-0.03736, -0.53955)
loop_1 = loop_1.lineTo(-0.00202, -0.54284)
loop_1 = loop_1.lineTo(-0.31282, -0.54452)
loop_1 = loop_1.lineTo(-0.31282, -0.41975)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_3_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_3_interval_1.stl')