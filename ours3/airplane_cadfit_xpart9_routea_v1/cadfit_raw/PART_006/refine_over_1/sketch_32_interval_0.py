import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81962, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70731, 0.2541)
loop_1 = loop_1.lineTo(-0.26764, 0.13272)
loop_1 = loop_1.lineTo(-0.3471, 0.14226)
loop_1 = loop_1.threePointArc((-0.38445, 0.14667), (-0.42294, 0.15179))
loop_1 = loop_1.threePointArc((-0.45115, 0.15591), (-0.47966, 0.16293))
loop_1 = loop_1.lineTo(-0.53247, 0.17633)
loop_1 = loop_1.lineTo(-0.56404, 0.18422)
loop_1 = loop_1.threePointArc((-0.59123, 0.19132), (-0.61725, 0.19706))
loop_1 = loop_1.lineTo(-0.64988, 0.20434)
loop_1 = loop_1.threePointArc((-0.65624, 0.20559), (-0.66208, 0.20643))
loop_1 = loop_1.lineTo(-0.68218, 0.20523)
loop_1 = loop_1.lineTo(-0.70348, 0.19869)
loop_1 = loop_1.lineTo(-0.72257, 0.19009)
loop_1 = loop_1.lineTo(-0.7074, 0.25377)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_32_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_32_interval_0.stl')