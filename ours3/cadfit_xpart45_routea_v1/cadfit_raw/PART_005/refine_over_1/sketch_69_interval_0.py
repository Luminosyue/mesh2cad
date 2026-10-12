import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.49918, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.87296, 0.2117)
loop_1 = loop_1.lineTo(0.8726, -0.21236)
loop_1 = loop_1.lineTo(0.87145, -0.15733)
loop_1 = loop_1.lineTo(0.86005, -0.10695)
loop_1 = loop_1.lineTo(0.8449, -0.09012)
loop_1 = loop_1.lineTo(0.79389, -0.05848)
loop_1 = loop_1.lineTo(0.77427, -0.00359)
loop_1 = loop_1.lineTo(0.79071, 0.00691)
loop_1 = loop_1.lineTo(0.82974, 0.0438)
loop_1 = loop_1.threePointArc((0.83956, 0.05631), (0.84335, 0.06387))
loop_1 = loop_1.threePointArc((0.8516, 0.08222), (0.8606, 0.10077))
loop_1 = loop_1.lineTo(0.87133, 0.15399)
loop_1 = loop_1.lineTo(0.87272, 0.20325)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.21)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_69_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_69_interval_0.stl')