import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.13069, -0.93026, 0.04684), normal=(-0.14078, 0.98944, 0.0345), xDir=(0.99003, 0.14087, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26742, 0.27165)
loop_1 = loop_1.lineTo(-0.26962, 0.2606)
loop_1 = loop_1.lineTo(-0.28256, 0.26478)
loop_1 = loop_1.lineTo(-0.28588, 0.15205)
loop_1 = loop_1.lineTo(0.31414, 0.13449)
loop_1 = loop_1.lineTo(0.33692, 0.21998)
loop_1 = loop_1.lineTo(0.33233, 0.24799)
loop_1 = loop_1.lineTo(0.31538, 0.24711)
loop_1 = loop_1.lineTo(0.30265, 0.24838)
loop_1 = loop_1.lineTo(0.26898, 0.25595)
loop_1 = loop_1.lineTo(0.19155, 0.25822)
loop_1 = loop_1.lineTo(0.16445, 0.24928)
loop_1 = loop_1.lineTo(-0.07142, 0.26591)
loop_1 = loop_1.lineTo(-0.10858, 0.26394)
loop_1 = loop_1.lineTo(-0.26016, 0.27144)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_38_interval_0.stl')