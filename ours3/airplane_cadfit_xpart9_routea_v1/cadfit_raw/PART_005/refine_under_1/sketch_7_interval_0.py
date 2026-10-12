import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.11, -0.35124, 0.01775), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.82006, 0.0177)
loop_1 = loop_1.threePointArc((0.84913, 0.02643), (0.87978, 0.03423))
loop_1 = loop_1.lineTo(0.91653, 0.0444)
loop_1 = loop_1.threePointArc((0.92437, 0.04588), (0.93166, 0.04759))
loop_1 = loop_1.threePointArc((0.96905, 0.05404), (1.0017, 0.05879))
loop_1 = loop_1.lineTo(1.05665, 0.068)
loop_1 = loop_1.lineTo(1.15088, 0.08384)
loop_1 = loop_1.threePointArc((1.19625, 0.09196), (1.23949, 0.10115))
loop_1 = loop_1.lineTo(1.26629, 0.10936)
loop_1 = loop_1.lineTo(0.31067, 0.10853)
loop_1 = loop_1.threePointArc((0.31363, 0.09854), (0.31331, 0.09286))
loop_1 = loop_1.lineTo(0.31036, 0.06119)
loop_1 = loop_1.lineTo(0.30409, 0.03775)
loop_1 = loop_1.lineTo(0.81975, 0.03694)
loop_1 = loop_1.lineTo(0.82005, 0.01776)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_7_interval_0.stl')