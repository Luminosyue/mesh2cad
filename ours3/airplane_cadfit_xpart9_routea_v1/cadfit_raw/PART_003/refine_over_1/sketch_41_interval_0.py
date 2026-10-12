import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.83208, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17029, 0.26901)
loop_1 = loop_1.lineTo(-0.22814, 0.19267)
loop_1 = loop_1.lineTo(-0.15142, 0.1364)
loop_1 = loop_1.threePointArc((-0.15919, 0.14886), (-0.16711, 0.16181))
loop_1 = loop_1.lineTo(-0.17687, 0.17837)
loop_1 = loop_1.lineTo(-0.18838, 0.21345)
loop_1 = loop_1.lineTo(-0.18243, 0.24867)
loop_1 = loop_1.lineTo(-0.17035, 0.26891)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_41_interval_0.stl')