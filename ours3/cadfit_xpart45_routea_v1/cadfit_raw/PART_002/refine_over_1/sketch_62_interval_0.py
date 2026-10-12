import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.39412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.37591, -0.50052)
loop_1 = loop_1.threePointArc((0.36939, -0.52229), (0.36183, -0.54473))
loop_1 = loop_1.lineTo(0.35734, -0.56199)
loop_1 = loop_1.lineTo(0.37375, -0.509)
loop_1 = loop_1.lineTo(0.34407, -0.61951)
loop_1 = loop_1.threePointArc((0.34219, -0.63069), (0.34073, -0.6412))
loop_1 = loop_1.lineTo(0.33392, -0.73808)
loop_1 = loop_1.lineTo(0.34016, -0.76628)
loop_1 = loop_1.lineTo(0.35442, -0.78588)
loop_1 = loop_1.lineTo(0.37338, -0.80818)
loop_1 = loop_1.lineTo(0.37655, -0.4992)
loop_1 = loop_1.threePointArc((0.37852, -0.49266), (0.37993, -0.48654))
loop_1 = loop_1.lineTo(0.37605, -0.50053)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_62_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_62_interval_0.stl')