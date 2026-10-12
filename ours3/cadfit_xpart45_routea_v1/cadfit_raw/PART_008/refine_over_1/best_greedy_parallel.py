import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.6664, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.96516, 0.34812)
loop_1 = loop_1.lineTo(0.96668, 0.27473)
loop_1 = loop_1.lineTo(0.96023, 0.28506)
loop_1 = loop_1.threePointArc((0.94334, 0.2977), (0.92739, 0.30893))
loop_1 = loop_1.lineTo(0.86836, 0.31381)
loop_1 = loop_1.lineTo(0.5949, 0.31276)
loop_1 = loop_1.lineTo(0.4919, 0.31241)
loop_1 = loop_1.threePointArc((0.35337, 0.31152), (0.20988, 0.31179))
loop_1 = loop_1.lineTo(0.04495, 0.31247)
loop_1 = loop_1.lineTo(-0.11535, 0.31265)
loop_1 = loop_1.lineTo(-0.1439, 0.3134)
loop_1 = loop_1.lineTo(0.96435, 0.34809)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_008/refine_over_1/sketch_7_interval_0.stl')