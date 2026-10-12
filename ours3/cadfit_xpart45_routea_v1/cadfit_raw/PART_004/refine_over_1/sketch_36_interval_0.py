import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.36141, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18558, 0.8)
loop_1 = loop_1.lineTo(-0.05177, 0.79965)
loop_1 = loop_1.lineTo(-0.08156, 0.7856)
loop_1 = loop_1.lineTo(-0.10546, 0.77107)
loop_1 = loop_1.lineTo(-0.1163, 0.77446)
loop_1 = loop_1.lineTo(-0.14047, 0.77264)
loop_1 = loop_1.threePointArc((-0.15511, 0.7809), (-0.1692, 0.78857))
loop_1 = loop_1.lineTo(-0.18558, 0.8)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_36_interval_0.stl')