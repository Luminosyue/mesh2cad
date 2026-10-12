import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.38207, -0.82861, 0.01861), normal=(0.41839, -0.90827, 9e-05), xDir=(-0.90827, -0.41839, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.273, 0.53507)
loop_1 = loop_1.lineTo(-0.28294, 0.51244)
loop_1 = loop_1.lineTo(-0.29289, 0.4841)
loop_1 = loop_1.lineTo(-0.30195, 0.44677)
loop_1 = loop_1.lineTo(-0.30192, 0.53882)
loop_1 = loop_1.lineTo(-0.27074, 0.53882)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_10_interval_0.stl')