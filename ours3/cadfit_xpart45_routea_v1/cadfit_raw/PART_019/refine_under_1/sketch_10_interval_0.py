import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.02441, 0.13269, -0.94991), normal=(-0.00024, 0.00879, 0.99996), xDir=(0.0, 0.99996, -0.00879))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86071, 0.33087)
loop_1 = loop_1.lineTo(0.58935, 0.29413)
loop_1 = loop_1.lineTo(0.58935, -0.40226)
loop_1 = loop_1.lineTo(-0.86071, -0.4286)
loop_1 = loop_1.lineTo(-0.86071, 0.30913)
loop_1 = loop_1.lineTo(-0.86071, 0.33087)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_10_interval_0.stl')