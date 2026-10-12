import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.15286, -0.05395, 0.24874), normal=(-0.25797, -0.01362, -0.96606), xDir=(0.0, -0.9999, 0.01409))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05281, 0.71817)
loop_1 = loop_1.lineTo(0.00122, 0.72099)
loop_1 = loop_1.lineTo(0.0042, 0.73839)
loop_1 = loop_1.lineTo(0.00727, 0.77482)
loop_1 = loop_1.lineTo(0.0064, 0.78913)
loop_1 = loop_1.threePointArc((0.00467, 0.8157), (0.00118, 0.84102))
loop_1 = loop_1.lineTo(-0.00389, 0.87405)
loop_1 = loop_1.lineTo(0.0072, -0.89699)
loop_1 = loop_1.lineTo(0.04693, -0.89768)
loop_1 = loop_1.lineTo(0.05278, 0.70982)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.15)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_15_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_15_interval_0.stl')