import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.22708, 0.05689, -0.36535), normal=(0.02357, -0.65303, 0.75696), xDir=(-0.99935, -0.03607, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.49859, -0.17421)
loop_1 = loop_1.lineTo(0.34605, -0.17421)
loop_1 = loop_1.threePointArc((0.34631, -0.1943), (0.34695, -0.21073))
loop_1 = loop_1.lineTo(0.34922, -0.23266)
loop_1 = loop_1.threePointArc((0.35098, -0.24161), (0.35237, -0.24827))
loop_1 = loop_1.lineTo(0.3915, -0.27048)
loop_1 = loop_1.lineTo(0.40885, -0.27068)
loop_1 = loop_1.lineTo(0.43183, -0.26992)
loop_1 = loop_1.threePointArc((0.43898, -0.26955), (0.44584, -0.26911))
loop_1 = loop_1.lineTo(0.4592, -0.26732)
loop_1 = loop_1.lineTo(0.47678, -0.26183)
loop_1 = loop_1.lineTo(0.487, -0.25172)
loop_1 = loop_1.lineTo(0.49596, -0.22489)
loop_1 = loop_1.threePointArc((0.49707, -0.20257), (0.49838, -0.17934))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_3_interval_0.stl')