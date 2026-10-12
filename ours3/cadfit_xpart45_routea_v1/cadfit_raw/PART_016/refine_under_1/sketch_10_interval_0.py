import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2463, 0.80978, -0.04933), normal=(0.32593, -0.94536, 0.0075), xDir=(-0.94539, -0.32594, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17517, 0.10232)
loop_1 = loop_1.lineTo(-0.16941, 0.0868)
loop_1 = loop_1.lineTo(-0.15848, 0.04691)
loop_1 = loop_1.lineTo(-0.15692, 0.03665)
loop_1 = loop_1.lineTo(-0.14995, 0.00622)
loop_1 = loop_1.lineTo(-0.14877, -0.00662)
loop_1 = loop_1.lineTo(-0.14443, -0.03487)
loop_1 = loop_1.lineTo(-0.1433, -0.04665)
loop_1 = loop_1.threePointArc((-0.14391, -0.06939), (-0.14452, -0.08983))
loop_1 = loop_1.lineTo(-0.14659, -0.10312)
loop_1 = loop_1.lineTo(-0.15439, -0.13301)
loop_1 = loop_1.lineTo(-0.16972, -0.17618)
loop_1 = loop_1.threePointArc((-0.1751, -0.19295), (-0.17917, -0.20752))
loop_1 = loop_1.lineTo(-0.17806, 0.10801)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_10_interval_0.stl')