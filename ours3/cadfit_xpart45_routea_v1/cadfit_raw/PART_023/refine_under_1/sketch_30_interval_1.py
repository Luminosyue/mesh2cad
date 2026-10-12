import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49739, -0.03021, 0.03135), normal=(0.00466, -0.99999, 1e-05), xDir=(-0.99999, -0.00466, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10597, -0.22116)
loop_1 = loop_1.lineTo(-0.12895, -0.23083)
loop_1 = loop_1.lineTo(-0.1459, -0.25852)
loop_1 = loop_1.lineTo(-0.14712, -0.28404)
loop_1 = loop_1.lineTo(-0.13602, -0.30802)
loop_1 = loop_1.lineTo(-0.10456, -0.32609)
loop_1 = loop_1.lineTo(-0.08024, -0.31579)
loop_1 = loop_1.lineTo(-0.05564, -0.28526)
loop_1 = loop_1.lineTo(-0.05251, -0.2602)
loop_1 = loop_1.lineTo(-0.06815, -0.23294)
loop_1 = loop_1.lineTo(-0.10175, -0.22083)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_30_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_30_interval_1.stl')