import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.56369), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.2853, 0.83779)
loop_1 = loop_1.threePointArc((-0.27489, 0.8352), (-0.2641, 0.83231))
loop_1 = loop_1.threePointArc((-0.23859, 0.80997), (-0.22183, 0.79266))
loop_1 = loop_1.lineTo(-0.20537, 0.7648)
loop_1 = loop_1.lineTo(-0.19648, 0.75309)
loop_1 = loop_1.lineTo(-0.1858, 0.74)
loop_1 = loop_1.lineTo(-0.15736, 0.73467)
loop_1 = loop_1.threePointArc((-0.13053, 0.73467), (-0.11123, 0.73589))
loop_1 = loop_1.lineTo(-0.10948, 0.83778)
loop_1 = loop_1.lineTo(-0.28513, 0.83784)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.23)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_52_interval_0.stl')