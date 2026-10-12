import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.74145, -0.57279, -0.01612), normal=(-0.98286, 0.18417, 0.00829), xDir=(0.18418, 0.98289, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.72831, 0.13924)
loop_1 = loop_1.threePointArc((0.74446, 0.14139), (0.75993, 0.14367))
loop_1 = loop_1.threePointArc((0.78799, 0.14714), (0.8119, 0.15062))
loop_1 = loop_1.threePointArc((0.83344, 0.1532), (0.85109, 0.15566))
loop_1 = loop_1.lineTo(0.86762, 0.1576)
loop_1 = loop_1.lineTo(0.88091, 0.15889)
loop_1 = loop_1.lineTo(0.89816, 0.16103)
loop_1 = loop_1.threePointArc((0.91746, 0.16321), (0.93253, 0.165))
loop_1 = loop_1.lineTo(0.9535, 0.16541)
loop_1 = loop_1.threePointArc((0.96447, 0.1613), (0.97392, 0.15793))
loop_1 = loop_1.threePointArc((0.98665, 0.15119), (0.99629, 0.1462))
loop_1 = loop_1.lineTo(1.0151, 0.13113)
loop_1 = loop_1.lineTo(1.00385, 0.14328)
loop_1 = loop_1.lineTo(0.99441, 0.21544)
loop_1 = loop_1.lineTo(0.71425, 0.13724)
loop_1 = loop_1.lineTo(0.7256, 0.13887)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.75)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_28_interval_0.stl')