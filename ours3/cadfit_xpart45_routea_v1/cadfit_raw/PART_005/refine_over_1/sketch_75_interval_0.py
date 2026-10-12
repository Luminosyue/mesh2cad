import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.51069, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.85824, 0.15162)
loop_1 = loop_1.lineTo(0.85776, -0.15596)
loop_1 = loop_1.threePointArc((0.85466, -0.13087), (0.85141, -0.10704))
loop_1 = loop_1.threePointArc((0.84622, -0.10075), (0.84135, -0.09421))
loop_1 = loop_1.lineTo(0.80675, -0.06202)
loop_1 = loop_1.lineTo(0.79524, -0.05538)
loop_1 = loop_1.threePointArc((0.78604, -0.02758), (0.77875, -0.00363))
loop_1 = loop_1.lineTo(0.79951, 0.02061)
loop_1 = loop_1.threePointArc((0.8113, 0.03552), (0.82202, 0.05002))
loop_1 = loop_1.threePointArc((0.83453, 0.07492), (0.84775, 0.10047))
loop_1 = loop_1.threePointArc((0.85305, 0.12661), (0.85818, 0.1514))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_75_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_75_interval_0.stl')