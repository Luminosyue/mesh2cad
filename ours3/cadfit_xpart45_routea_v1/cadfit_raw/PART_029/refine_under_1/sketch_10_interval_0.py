import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.19377, -0.0794, 0.19482), normal=(-0.0, -0.78921, -0.61412), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(1.1692, 0.34725)
loop_1 = loop_1.lineTo(1.17024, 0.33634)
loop_1 = loop_1.lineTo(1.16882, 0.32454)
loop_1 = loop_1.lineTo(0.96544, 0.31973)
loop_1 = loop_1.lineTo(0.96426, 0.33025)
loop_1 = loop_1.lineTo(0.9654, 0.35229)
loop_1 = loop_1.lineTo(1.16592, 0.35229)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.16)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_10_interval_0.stl')