import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.2943, -0.23845, 0.7793), normal=(-0.23256, 0.00054, 0.97258), xDir=(0.0, 1.0, -0.00056))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.3652, 0.34521)
loop_1 = loop_1.lineTo(0.3652, 0.27007)
loop_1 = loop_1.lineTo(0.48646, 0.26993)
loop_1 = loop_1.lineTo(0.47402, 0.27904)
loop_1 = loop_1.lineTo(0.45328, 0.28775)
loop_1 = loop_1.lineTo(0.43424, 0.31306)
loop_1 = loop_1.lineTo(0.41685, 0.3236)
loop_1 = loop_1.lineTo(0.39949, 0.33264)
loop_1 = loop_1.lineTo(0.39033, 0.34282)
loop_1 = loop_1.lineTo(0.38017, 0.34324)
loop_1 = loop_1.lineTo(0.36698, 0.34498)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_16_interval_0.stl')