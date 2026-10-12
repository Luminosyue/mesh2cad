import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.64579, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.4877, -0.09732)
loop_1 = loop_1.threePointArc((0.47712, -0.10558), (0.46588, -0.11391))
loop_1 = loop_1.lineTo(0.44938, -0.12473)
loop_1 = loop_1.lineTo(0.42834, -0.13427)
loop_1 = loop_1.threePointArc((0.41371, -0.13862), (0.4074, -0.13997))
loop_1 = loop_1.threePointArc((0.39155, -0.14106), (0.3837, -0.14109))
loop_1 = loop_1.lineTo(0.42512, -0.16821)
loop_1 = loop_1.lineTo(0.47322, -0.11447)
loop_1 = loop_1.lineTo(0.49036, -0.09486)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_24_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_24_interval_1.stl')