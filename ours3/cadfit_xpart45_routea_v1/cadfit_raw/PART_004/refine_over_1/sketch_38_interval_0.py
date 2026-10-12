import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.79959), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04521, -0.41309)
loop_1 = loop_1.lineTo(0.13028, -0.4127)
loop_1 = loop_1.lineTo(0.13004, -0.37973)
loop_1 = loop_1.lineTo(0.10637, -0.38864)
loop_1 = loop_1.lineTo(0.07115, -0.39915)
loop_1 = loop_1.lineTo(0.03669, -0.40677)
loop_1 = loop_1.threePointArc((0.01946, -0.40891), (0.00163, -0.41098))
loop_1 = loop_1.threePointArc((-0.01693, -0.41184), (-0.0346, -0.41287))
loop_1 = loop_1.lineTo(-0.04508, -0.41309)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.4)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_38_interval_0.stl')