import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.31919, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.19671, 0.8)
loop_1 = loop_1.lineTo(-0.2617, 0.79983)
loop_1 = loop_1.threePointArc((-0.25504, 0.79111), (-0.24847, 0.78295))
loop_1 = loop_1.threePointArc((-0.23981, 0.77979), (-0.23169, 0.77745))
loop_1 = loop_1.lineTo(-0.21273, 0.77195)
loop_1 = loop_1.threePointArc((-0.20938, 0.77694), (-0.20586, 0.78207))
loop_1 = loop_1.lineTo(-0.19755, 0.79403)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_25_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_25_interval_0.stl')