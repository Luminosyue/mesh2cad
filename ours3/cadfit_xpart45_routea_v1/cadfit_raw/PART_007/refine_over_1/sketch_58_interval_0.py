import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.42348), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99, 0.60345)
loop_1 = loop_1.lineTo(-0.98972, 0.50658)
loop_1 = loop_1.lineTo(-0.98495, 0.53362)
loop_1 = loop_1.lineTo(-0.97521, 0.56569)
loop_1 = loop_1.lineTo(-0.96575, 0.57967)
loop_1 = loop_1.lineTo(-0.93371, 0.60345)
loop_1 = loop_1.lineTo(-0.98991, 0.60345)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_58_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_58_interval_0.stl')