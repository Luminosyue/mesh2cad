import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40615, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31308, 0.8)
loop_1 = loop_1.lineTo(0.25647, 0.76545)
loop_1 = loop_1.lineTo(0.27228, 0.75862)
loop_1 = loop_1.lineTo(0.2942, 0.72991)
loop_1 = loop_1.threePointArc((0.30012, 0.70321), (0.30177, 0.68195))
loop_1 = loop_1.lineTo(0.30444, 0.64862)
loop_1 = loop_1.lineTo(0.30901, 0.57463)
loop_1 = loop_1.threePointArc((0.31081, 0.54558), (0.31173, 0.51552))
loop_1 = loop_1.lineTo(0.31308, 0.48653)
loop_1 = loop_1.lineTo(0.31308, 0.79977)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_20_interval_0.stl')