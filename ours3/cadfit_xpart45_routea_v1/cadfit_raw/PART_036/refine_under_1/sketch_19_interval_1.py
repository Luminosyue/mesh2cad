import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.83299, -0.02804, -0.09632), normal=(0.99999, -0.00495, -0.00023), xDir=(-0.00495, -0.99999, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18479, 0.15868)
loop_1 = loop_1.lineTo(-0.20222, 0.15743)
loop_1 = loop_1.lineTo(-0.21803, 0.15207)
loop_1 = loop_1.lineTo(-0.23345, 0.13477)
loop_1 = loop_1.threePointArc((-0.23536, 0.12493), (-0.23681, 0.11735))
loop_1 = loop_1.lineTo(-0.23458, 0.09992)
loop_1 = loop_1.threePointArc((-0.23223, 0.09008), (-0.23041, 0.08251))
loop_1 = loop_1.lineTo(-0.22524, 0.06509)
loop_1 = loop_1.lineTo(-0.22237, 0.10695)
loop_1 = loop_1.lineTo(-0.10782, 0.10635)
loop_1 = loop_1.lineTo(-0.12064, 0.1189)
loop_1 = loop_1.threePointArc((-0.12806, 0.12663), (-0.13569, 0.13479))
loop_1 = loop_1.lineTo(-0.14995, 0.14869)
loop_1 = loop_1.lineTo(-0.16738, 0.15708)
loop_1 = loop_1.lineTo(-0.18479, 0.15868)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_19_interval_1.stl')