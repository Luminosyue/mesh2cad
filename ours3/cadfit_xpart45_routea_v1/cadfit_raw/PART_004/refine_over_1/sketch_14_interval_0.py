import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03608, 0.13831, -0.21579), normal=(0.01246, -0.99992, -0.00166), xDir=(-0.99992, -0.01246, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.07071, 0.7817)
loop_1 = loop_1.lineTo(0.19942, 0.62705)
loop_1 = loop_1.lineTo(0.1985, 0.67657)
loop_1 = loop_1.lineTo(0.19633, 0.72207)
loop_1 = loop_1.threePointArc((0.1884, 0.73927), (0.1811, 0.75345))
loop_1 = loop_1.lineTo(0.1628, 0.7655)
loop_1 = loop_1.threePointArc((0.15382, 0.76933), (0.14457, 0.77356))
loop_1 = loop_1.lineTo(0.13385, 0.77752)
loop_1 = loop_1.lineTo(0.09759, 0.78132)
loop_1 = loop_1.lineTo(0.07071, 0.7817)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.39)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_14_interval_0.stl')