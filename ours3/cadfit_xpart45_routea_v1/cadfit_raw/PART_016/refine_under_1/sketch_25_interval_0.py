import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06267, 0.76314, -0.296), normal=(0.0, -0.88735, 0.46109), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.12477, -0.49637)
loop_1 = loop_1.lineTo(-0.17527, -0.49637)
loop_1 = loop_1.lineTo(-0.16762, -0.50798)
loop_1 = loop_1.lineTo(-0.13689, -0.53166)
loop_1 = loop_1.lineTo(-0.12542, -0.54275)
loop_1 = loop_1.lineTo(-0.10595, -0.54857)
loop_1 = loop_1.lineTo(-0.08127, -0.55774)
loop_1 = loop_1.lineTo(-0.05839, -0.55778)
loop_1 = loop_1.lineTo(-0.0381, -0.55897)
loop_1 = loop_1.threePointArc((-0.01519, -0.55845), (0.00508, -0.55828))
loop_1 = loop_1.threePointArc((0.02867, -0.55719), (0.04825, -0.55609))
loop_1 = loop_1.lineTo(0.08764, -0.54275)
loop_1 = loop_1.lineTo(0.09853, -0.5316)
loop_1 = loop_1.lineTo(0.11698, -0.51033)
loop_1 = loop_1.lineTo(0.12321, -0.49916)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_25_interval_0.stl')