import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5006, -0.79503, 0.07342), normal=(-0.51809, -0.85532, 0.00012), xDir=(-0.85532, 0.51809, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.2904, -0.10684)
loop_1 = loop_1.lineTo(0.2905, -0.45676)
loop_1 = loop_1.lineTo(0.24563, -0.45676)
loop_1 = loop_1.lineTo(0.2611, -0.44867)
loop_1 = loop_1.threePointArc((0.26868, -0.42124), (0.27603, -0.39686))
loop_1 = loop_1.lineTo(0.27587, -0.38338)
loop_1 = loop_1.lineTo(0.27397, -0.345)
loop_1 = loop_1.threePointArc((0.27565, -0.30981), (0.27678, -0.27997))
loop_1 = loop_1.lineTo(0.27939, -0.24134)
loop_1 = loop_1.lineTo(0.28303, -0.18449)
loop_1 = loop_1.lineTo(0.28712, -0.13412)
loop_1 = loop_1.lineTo(0.28991, -0.11088)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_54_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_54_interval_0.stl')