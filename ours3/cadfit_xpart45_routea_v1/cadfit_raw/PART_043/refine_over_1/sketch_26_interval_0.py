import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.64729, -0.2398, -0.23729), normal=(0.00064, -0.00049, 1.0), xDir=(-0.0, 1.0, 0.00049))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40677, -0.15347)
loop_1 = loop_1.lineTo(-0.39362, -0.15891)
loop_1 = loop_1.lineTo(-0.15408, -0.42343)
loop_1 = loop_1.lineTo(-0.44162, -0.13141)
loop_1 = loop_1.lineTo(-0.41924, -0.1486)
loop_1 = loop_1.lineTo(-0.40677, -0.15347)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_26_interval_0.stl')