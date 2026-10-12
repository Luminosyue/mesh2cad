import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.00724, 0.11352, -0.22696), normal=(0.02791, -0.62791, 0.77778), xDir=(-0.99901, -0.04441, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.92181, -0.03463)
loop_1 = loop_1.lineTo(-0.96294, -0.03463)
loop_1 = loop_1.lineTo(-0.96516, -0.05817)
loop_1 = loop_1.lineTo(-0.96403, -0.06834)
loop_1 = loop_1.lineTo(-0.95548, -0.08274)
loop_1 = loop_1.lineTo(-0.93004, -0.08762)
loop_1 = loop_1.lineTo(-0.92019, -0.05903)
loop_1 = loop_1.lineTo(-0.92152, -0.04822)
loop_1 = loop_1.lineTo(-0.92181, -0.03463)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_5_interval_0.stl')