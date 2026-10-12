import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.0048, 0.09174, 0.04775), normal=(-0.1889, -0.58283, -0.79033), xDir=(-0.95128, 0.30832, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94719, -0.2002)
loop_1 = loop_1.lineTo(0.94571, -0.21834)
loop_1 = loop_1.lineTo(0.94363, -0.23776)
loop_1 = loop_1.lineTo(0.94128, -0.2558)
loop_1 = loop_1.lineTo(0.93672, -0.2789)
loop_1 = loop_1.lineTo(0.93184, -0.30049)
loop_1 = loop_1.lineTo(0.92629, -0.32221)
loop_1 = loop_1.lineTo(0.92292, -0.33417)
loop_1 = loop_1.lineTo(0.86911, -0.3121)
loop_1 = loop_1.lineTo(0.88432, -0.3024)
loop_1 = loop_1.lineTo(0.90153, -0.28719)
loop_1 = loop_1.lineTo(0.92048, -0.26433)
loop_1 = loop_1.lineTo(0.93337, -0.24095)
loop_1 = loop_1.lineTo(0.94244, -0.21666)
loop_1 = loop_1.lineTo(0.94719, -0.2002)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_7_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_7_interval_0.stl')