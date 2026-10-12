import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.74846, -0.0082, -0.17893), normal=(0.0419, -0.01236, 0.99905), xDir=(-0.0, 0.99992, 0.01238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.02709, 0.31439)
loop_1 = loop_1.threePointArc((0.03395, 0.31562), (0.04051, 0.31693))
loop_1 = loop_1.lineTo(0.05425, 0.32358)
loop_1 = loop_1.lineTo(0.0637, 0.33884)
loop_1 = loop_1.lineTo(0.05985, 0.3494)
loop_1 = loop_1.threePointArc((0.05633, 0.3559), (0.0539, 0.35967))
loop_1 = loop_1.lineTo(0.03924, 0.37036)
loop_1 = loop_1.lineTo(0.02898, 0.37219)
loop_1 = loop_1.lineTo(-0.01215, 0.33541)
loop_1 = loop_1.lineTo(0.02618, 0.31488)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_18_interval_0.stl')