import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.20295, 0.69332, -0.05724), normal=(0.07617, -0.99709, 0.00262), xDir=(-0.99709, -0.07617, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14983, -0.11753)
loop_1 = loop_1.lineTo(-0.16844, -0.11481)
loop_1 = loop_1.lineTo(-0.16844, -0.12951)
loop_1 = loop_1.lineTo(-0.19284, -0.16225)
loop_1 = loop_1.lineTo(-0.20228, -0.21345)
loop_1 = loop_1.lineTo(-0.20022, 0.49018)
loop_1 = loop_1.lineTo(-0.17952, 0.49018)
loop_1 = loop_1.lineTo(-0.15019, -0.11012)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_5_interval_0.stl')