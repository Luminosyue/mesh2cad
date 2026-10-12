import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.52792, -0.09107, -0.04909), normal=(0.99998, -0.00591, -0.00178), xDir=(-0.00591, -0.99998, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16422, -0.01977)
loop_1 = loop_1.lineTo(-0.11963, -0.25965)
loop_1 = loop_1.lineTo(-0.1228, -0.23707)
loop_1 = loop_1.lineTo(-0.12254, -0.22263)
loop_1 = loop_1.lineTo(-0.12394, -0.20119)
loop_1 = loop_1.lineTo(-0.12233, -0.18561)
loop_1 = loop_1.lineTo(-0.12272, -0.16296)
loop_1 = loop_1.lineTo(-0.1241, -0.1486)
loop_1 = loop_1.threePointArc((-0.12984, -0.12731), (-0.13516, -0.10929))
loop_1 = loop_1.lineTo(-0.14705, -0.07456)
loop_1 = loop_1.lineTo(-0.15646, -0.04529)
loop_1 = loop_1.threePointArc((-0.16045, -0.03163), (-0.16359, -0.02101))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_19_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_19_interval_1.stl')