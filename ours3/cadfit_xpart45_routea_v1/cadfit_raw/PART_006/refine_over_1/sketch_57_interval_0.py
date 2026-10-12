import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.51909, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84087, 0.10422)
loop_1 = loop_1.lineTo(0.84045, -0.27569)
loop_1 = loop_1.threePointArc((0.83898, -0.23292), (0.83815, -0.18864))
loop_1 = loop_1.threePointArc((0.83755, -0.17335), (0.83684, -0.15896))
loop_1 = loop_1.threePointArc((0.83475, -0.13514), (0.83202, -0.11262))
loop_1 = loop_1.lineTo(0.81524, -0.08943)
loop_1 = loop_1.lineTo(0.79019, -0.06742)
loop_1 = loop_1.lineTo(0.77634, -0.05978)
loop_1 = loop_1.lineTo(0.76093, -0.02939)
loop_1 = loop_1.lineTo(0.74886, -0.00803)
loop_1 = loop_1.threePointArc((0.75781, -0.00151), (0.76598, 0.00486))
loop_1 = loop_1.lineTo(0.79306, 0.02774)
loop_1 = loop_1.lineTo(0.81029, 0.04469)
loop_1 = loop_1.threePointArc((0.81803, 0.05759), (0.82441, 0.07025))
loop_1 = loop_1.lineTo(0.83874, 0.09738)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_57_interval_0.stl')