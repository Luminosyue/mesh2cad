import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.99113, -0.12949, 0.039), normal=(0.99528, 0.09704, 0.00149), xDir=(0.09704, -0.99528, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31434, -0.11153)
loop_1 = loop_1.lineTo(-0.08869, -0.02809)
loop_1 = loop_1.lineTo(-0.05887, -0.02785)
loop_1 = loop_1.lineTo(-0.03919, -0.02903)
loop_1 = loop_1.threePointArc((-0.00367, -0.02862), (0.02912, -0.02854))
loop_1 = loop_1.lineTo(0.04529, -0.02977)
loop_1 = loop_1.lineTo(0.08682, -0.02926)
loop_1 = loop_1.lineTo(0.09737, -0.03059)
loop_1 = loop_1.lineTo(0.14449, -0.03209)
loop_1 = loop_1.lineTo(0.19506, -0.03534)
loop_1 = loop_1.lineTo(0.20618, -0.03739)
loop_1 = loop_1.lineTo(0.2536, -0.05272)
loop_1 = loop_1.lineTo(0.27857, -0.06212)
loop_1 = loop_1.lineTo(0.29712, -0.06832)
loop_1 = loop_1.lineTo(0.30393, -0.08486)
loop_1 = loop_1.lineTo(0.31289, -0.10784)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_23_interval_0.stl')