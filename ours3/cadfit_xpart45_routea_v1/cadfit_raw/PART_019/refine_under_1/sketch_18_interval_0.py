import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.81126, -0.04135, -0.47213), normal=(0.86333, -0.00027, 0.50464), xDir=(-0.00031, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.73792, 0.16437)
loop_1 = loop_1.lineTo(0.73816, -0.1641)
loop_1 = loop_1.lineTo(0.74329, -0.13174)
loop_1 = loop_1.lineTo(0.74766, -0.11465)
loop_1 = loop_1.lineTo(0.74734, -0.03838)
loop_1 = loop_1.lineTo(0.74883, -4e-05)
loop_1 = loop_1.lineTo(0.74956, 0.0111)
loop_1 = loop_1.lineTo(0.74739, 0.02165)
loop_1 = loop_1.lineTo(0.74935, 0.03301)
loop_1 = loop_1.lineTo(0.75106, 0.06124)
loop_1 = loop_1.lineTo(0.74915, 0.10133)
loop_1 = loop_1.lineTo(0.74397, 0.13312)
loop_1 = loop_1.lineTo(0.73844, 0.16164)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.9)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_18_interval_0.stl')