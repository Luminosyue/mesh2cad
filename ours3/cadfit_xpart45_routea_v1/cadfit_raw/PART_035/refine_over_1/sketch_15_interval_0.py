import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43205, 0.48535, 0.03648), normal=(0.95468, -0.29759, 0.00451), xDir=(-0.29759, -0.95469, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07786, 0.25635)
loop_1 = loop_1.lineTo(-0.09504, 0.25635)
loop_1 = loop_1.lineTo(-0.09511, 0.21426)
loop_1 = loop_1.lineTo(-0.09492, 0.18983)
loop_1 = loop_1.threePointArc((-0.09679, 0.17734), (-0.0985, 0.16655))
loop_1 = loop_1.threePointArc((-0.09913, 0.22618), (-0.09908, 0.28707))
loop_1 = loop_1.lineTo(-0.05846, 0.28707)
loop_1 = loop_1.lineTo(-0.07689, 0.25788)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_15_interval_0.stl')