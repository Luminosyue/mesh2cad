import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.07289, -0.05818, -0.05074), normal=(-0.25797, -0.01362, -0.96606), xDir=(0.0, -0.9999, 0.01409))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09097, 1.03353)
loop_1 = loop_1.lineTo(-0.11429, 1.052)
loop_1 = loop_1.lineTo(-0.14335, 1.066)
loop_1 = loop_1.lineTo(-0.18417, 1.07663)
loop_1 = loop_1.lineTo(-0.07605, 1.07657)
loop_1 = loop_1.lineTo(-0.07626, 1.01906)
loop_1 = loop_1.lineTo(-0.09097, 1.03353)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_14_interval_0.stl')