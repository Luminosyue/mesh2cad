import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.17446, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11445, 0.46195)
loop_1 = loop_1.lineTo(-0.12075, 0.45143)
loop_1 = loop_1.lineTo(-0.11871, 0.4368)
loop_1 = loop_1.lineTo(-0.09916, 0.4267)
loop_1 = loop_1.lineTo(-0.08494, 0.4307)
loop_1 = loop_1.lineTo(-0.07045, 0.44684)
loop_1 = loop_1.lineTo(-0.07463, 0.46086)
loop_1 = loop_1.lineTo(-0.09714, 0.47026)
loop_1 = loop_1.lineTo(-0.11445, 0.46195)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/sketch_23_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/sketch_23_interval_1.stl')