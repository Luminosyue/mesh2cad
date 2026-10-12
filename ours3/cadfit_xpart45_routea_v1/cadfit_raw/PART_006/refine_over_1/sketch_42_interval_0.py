import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.1778, -0.57018, -0.00502), normal=(-0.21566, 0.97647, -2e-05), xDir=(0.97647, 0.21566, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26163, -0.31153)
loop_1 = loop_1.lineTo(0.25887, -0.37957)
loop_1 = loop_1.threePointArc((0.25888, -0.40635), (0.25874, -0.43168))
loop_1 = loop_1.lineTo(0.25741, -0.4746)
loop_1 = loop_1.lineTo(0.25018, -0.49553)
loop_1 = loop_1.lineTo(0.23379, -0.52328)
loop_1 = loop_1.lineTo(0.22528, -0.53441)
loop_1 = loop_1.lineTo(0.26162, -0.53441)
loop_1 = loop_1.lineTo(0.26163, -0.314)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.12)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_42_interval_0.stl')