import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.00782, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02157, 0.35294)
loop_1 = loop_1.lineTo(-0.0227, 0.33779)
loop_1 = loop_1.lineTo(-0.02013, 0.31875)
loop_1 = loop_1.lineTo(-0.02052, 0.30769)
loop_1 = loop_1.lineTo(-0.02247, 0.2897)
loop_1 = loop_1.lineTo(-0.03646, 0.27739)
loop_1 = loop_1.lineTo(-0.05421, 0.28447)
loop_1 = loop_1.threePointArc((-0.05648, 0.29292), (-0.05851, 0.30168))
loop_1 = loop_1.lineTo(-0.05686, 0.3246)
loop_1 = loop_1.lineTo(-0.0636, 0.35147)
loop_1 = loop_1.lineTo(-0.06611, 0.38325)
loop_1 = loop_1.lineTo(-0.05231, 0.38683)
loop_1 = loop_1.lineTo(-0.0318, 0.39333)
loop_1 = loop_1.lineTo(-0.02157, 0.35294)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_43_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_042/sketch_43_interval_1.stl')