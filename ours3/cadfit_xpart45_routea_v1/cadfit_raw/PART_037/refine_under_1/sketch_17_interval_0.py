import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01874, -0.1014, 0.14392), normal=(-0.00027, 0.01138, -0.99994), xDir=(0.0, -0.99994, -0.01138))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01424, -0.66103)
loop_1 = loop_1.lineTo(0.01375, -0.67467)
loop_1 = loop_1.lineTo(0.00952, -0.68831)
loop_1 = loop_1.lineTo(-0.00744, -0.67909)
loop_1 = loop_1.lineTo(-0.01125, -0.66103)
loop_1 = loop_1.lineTo(-0.01103, -0.64739)
loop_1 = loop_1.lineTo(-0.00945, -0.63373)
loop_1 = loop_1.threePointArc((-0.00116, -0.62365), (0.0042, -0.62011))
loop_1 = loop_1.lineTo(0.0117, -0.63375)
loop_1 = loop_1.lineTo(0.01376, -0.64739)
loop_1 = loop_1.lineTo(0.01423, -0.66087)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_17_interval_0.stl')