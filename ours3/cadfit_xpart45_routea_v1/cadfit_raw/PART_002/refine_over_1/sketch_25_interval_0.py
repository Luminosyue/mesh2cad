import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0052, -0.28976, -0.3628), normal=(0.00015, 0.58735, -0.80933), xDir=(1.0, -0.00026, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01365, 0.15451)
loop_1 = loop_1.lineTo(0.06039, 0.15245)
loop_1 = loop_1.lineTo(0.10072, 0.14878)
loop_1 = loop_1.lineTo(0.16486, 0.14448)
loop_1 = loop_1.lineTo(0.1997, 0.14178)
loop_1 = loop_1.lineTo(0.21164, 0.14036)
loop_1 = loop_1.lineTo(0.23405, 0.13845)
loop_1 = loop_1.threePointArc((0.24566, 0.13557), (0.25473, 0.13309))
loop_1 = loop_1.lineTo(0.25472, 0.15347)
loop_1 = loop_1.lineTo(0.07224, 0.15347)
loop_1 = loop_1.lineTo(0.11937, 0.14829)
loop_1 = loop_1.lineTo(0.09738, 0.149)
loop_1 = loop_1.lineTo(0.05759, 0.15264)
loop_1 = loop_1.lineTo(0.0233, 0.15458)
loop_1 = loop_1.lineTo(-0.01264, 0.1545)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_25_interval_0.stl')