import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.17403, 0.20316)
loop_1 = loop_1.lineTo(0.1279, 0.16313)
loop_1 = loop_1.lineTo(0.14715, 0.14107)
loop_1 = loop_1.lineTo(0.16327, 0.14104)
loop_1 = loop_1.lineTo(0.18818, 0.16272)
loop_1 = loop_1.lineTo(0.18823, 0.18678)
loop_1 = loop_1.lineTo(0.17407, 0.20312)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.27)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_48_interval_0.stl')