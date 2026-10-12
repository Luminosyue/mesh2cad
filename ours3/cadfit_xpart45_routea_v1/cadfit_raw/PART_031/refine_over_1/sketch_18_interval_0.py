import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.05972, 0.3413, 0.3608), normal=(0.0, -0.9056, 0.42414), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98881, 0.6141)
loop_1 = loop_1.threePointArc((0.98166, 0.58853), (0.97374, 0.56203))
loop_1 = loop_1.lineTo(0.95619, 0.52314)
loop_1 = loop_1.lineTo(0.94777, 0.50705)
loop_1 = loop_1.lineTo(0.91358, 0.45206)
loop_1 = loop_1.threePointArc((0.91081, 0.42107), (0.90915, 0.39707))
loop_1 = loop_1.threePointArc((0.9316, 0.36805), (0.95171, 0.34209))
loop_1 = loop_1.lineTo(0.94688, 0.2871)
loop_1 = loop_1.threePointArc((0.94074, 0.24921), (0.935, 0.2157))
loop_1 = loop_1.lineTo(0.91025, 0.08702)
loop_1 = loop_1.threePointArc((0.91739, 0.11986), (0.92388, 0.154))
loop_1 = loop_1.threePointArc((0.93909, 0.23182), (0.9519, 0.30161))
loop_1 = loop_1.threePointArc((0.96169, 0.36361), (0.96928, 0.41836))
loop_1 = loop_1.lineTo(0.97932, 0.50348)
loop_1 = loop_1.threePointArc((0.9847, 0.55988), (0.98845, 0.60893))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_18_interval_0.stl')