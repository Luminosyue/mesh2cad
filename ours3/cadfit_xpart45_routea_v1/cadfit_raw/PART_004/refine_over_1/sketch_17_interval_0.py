import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03608, 0.13831, -0.21579), normal=(0.01246, -0.99992, -0.00166), xDir=(-0.99992, -0.01246, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05512, 0.77945)
loop_1 = loop_1.lineTo(-0.07345, 0.77201)
loop_1 = loop_1.lineTo(-0.10302, 0.76388)
loop_1 = loop_1.lineTo(-0.1187, 0.75219)
loop_1 = loop_1.lineTo(-0.12786, 0.72669)
loop_1 = loop_1.threePointArc((-0.12959, 0.7204), (-0.13099, 0.71429))
loop_1 = loop_1.lineTo(-0.13171, 0.6499)
loop_1 = loop_1.lineTo(-0.02009, 0.78144)
loop_1 = loop_1.lineTo(-0.05512, 0.77945)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_17_interval_0.stl')