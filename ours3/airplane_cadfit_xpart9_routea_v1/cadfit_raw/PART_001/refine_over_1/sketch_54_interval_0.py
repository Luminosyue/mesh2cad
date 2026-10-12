import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.97954, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.31145, -0.09634)
loop_1 = loop_1.threePointArc((-0.28903, -0.10419), (-0.2674, -0.11139))
loop_1 = loop_1.threePointArc((-0.23734, -0.12083), (-0.20638, -0.13119))
loop_1 = loop_1.lineTo(-0.1772, -0.14152)
loop_1 = loop_1.threePointArc((-0.15767, -0.14788), (-0.13874, -0.15273))
loop_1 = loop_1.lineTo(-0.0922, -0.16385)
loop_1 = loop_1.lineTo(-0.31145, -0.16554)
loop_1 = loop_1.lineTo(-0.31145, -0.09653)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_54_interval_0.stl')