import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03961, -0.55615, -0.70103), normal=(1e-05, 0.95255, -0.30437), xDir=(1.0, -1e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18427, -1.57593)
loop_1 = loop_1.lineTo(-0.36871, -1.49927)
loop_1 = loop_1.threePointArc((-0.31973, -1.5245), (-0.27385, -1.54679))
loop_1 = loop_1.threePointArc((-0.24621, -1.5589), (-0.22685, -1.56601))
loop_1 = loop_1.lineTo(-0.20954, -1.5717)
loop_1 = loop_1.lineTo(-0.1739, -1.57987)
loop_1 = loop_1.lineTo(-0.08558, -1.59416)
loop_1 = loop_1.lineTo(-0.0596, -1.59785)
loop_1 = loop_1.lineTo(-0.02096, -1.59897)
loop_1 = loop_1.lineTo(-0.00176, -1.59754)
loop_1 = loop_1.lineTo(0.34038, -1.59754)
loop_1 = loop_1.lineTo(0.33998, -1.49905)
loop_1 = loop_1.threePointArc((0.324, -1.50916), (0.30971, -1.51667))
loop_1 = loop_1.threePointArc((0.28674, -1.52879), (0.26442, -1.53885))
loop_1 = loop_1.threePointArc((0.25446, -1.54329), (0.24952, -1.54538))
loop_1 = loop_1.lineTo(-0.17841, -1.57552)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_10_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_10_interval_2.stl')