import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.61905, -0.28208, 0.01235), normal=(0.9998, -0.01979, 0.0), xDir=(-0.01979, -0.9998, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.37809, -0.48236)
loop_1 = loop_1.lineTo(-0.37809, -0.55193)
loop_1 = loop_1.lineTo(-0.09853, -0.54881)
loop_1 = loop_1.lineTo(-0.11294, -0.54239)
loop_1 = loop_1.lineTo(-0.15008, -0.52957)
loop_1 = loop_1.lineTo(-0.16963, -0.52475)
loop_1 = loop_1.lineTo(-0.18265, -0.52188)
loop_1 = loop_1.threePointArc((-0.1987, -0.51792), (-0.21418, -0.5144))
loop_1 = loop_1.threePointArc((-0.23367, -0.50949), (-0.24938, -0.50608))
loop_1 = loop_1.lineTo(-0.26855, -0.50193)
loop_1 = loop_1.threePointArc((-0.28894, -0.49687), (-0.30532, -0.49297))
loop_1 = loop_1.lineTo(-0.32047, -0.48998)
loop_1 = loop_1.lineTo(-0.33071, -0.48817)
loop_1 = loop_1.lineTo(-0.36749, -0.48544)
loop_1 = loop_1.lineTo(-0.37809, -0.48236)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_29_interval_0.stl')