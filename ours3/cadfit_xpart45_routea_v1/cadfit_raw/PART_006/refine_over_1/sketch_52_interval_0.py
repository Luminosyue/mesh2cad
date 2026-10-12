import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05641, -0.51, 0.13142), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.40263, -0.28143)
loop_1 = loop_1.lineTo(-0.55046, -0.29012)
loop_1 = loop_1.lineTo(-0.58405, -0.33226)
loop_1 = loop_1.lineTo(-0.59192, -0.3446)
loop_1 = loop_1.threePointArc((-0.60983, -0.37098), (-0.62916, -0.39799))
loop_1 = loop_1.lineTo(-0.61716, -0.39794)
loop_1 = loop_1.lineTo(0.51694, -0.3975)
loop_1 = loop_1.lineTo(0.49671, -0.36937)
loop_1 = loop_1.lineTo(0.48272, -0.34467)
loop_1 = loop_1.lineTo(0.45843, -0.29266)
loop_1 = loop_1.lineTo(0.40796, -0.28322)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_52_interval_0.stl')