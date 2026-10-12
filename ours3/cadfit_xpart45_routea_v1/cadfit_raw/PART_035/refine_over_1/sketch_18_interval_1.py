import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.4031, 0.31629, -0.03225), normal=(0.05916, 0.99825, -0.00036), xDir=(0.99825, -0.05916, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29203, 0.00472)
loop_1 = loop_1.lineTo(-0.2822, -0.26937)
loop_1 = loop_1.lineTo(-0.274, -0.28268)
loop_1 = loop_1.lineTo(-0.29573, -0.28268)
loop_1 = loop_1.lineTo(-0.29576, 0.10775)
loop_1 = loop_1.lineTo(-0.29247, 0.00325)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_18_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_18_interval_1.stl')