import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.59838, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70934, 0.19701)
loop_1 = loop_1.lineTo(0.15993, 0.2054)
loop_1 = loop_1.lineTo(0.18244, 0.20601)
loop_1 = loop_1.lineTo(0.49265, 0.21037)
loop_1 = loop_1.lineTo(-0.39909, 0.20203)
loop_1 = loop_1.lineTo(-0.68549, 0.19936)
loop_1 = loop_1.threePointArc((-0.69851, 0.19933), (-0.70912, 0.19715))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_50_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_50_interval_2.stl')