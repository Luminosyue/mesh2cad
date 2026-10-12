import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.36109, -0.03505, -0.83514), normal=(0.38651, -0.0014, 0.92228), xDir=(-0.0, 1.0, 0.00152))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.7363, -0.44377)
loop_1 = loop_1.lineTo(0.35529, -0.43566)
loop_1 = loop_1.lineTo(0.36619, -0.43656)
loop_1 = loop_1.lineTo(0.43908, -0.43584)
loop_1 = loop_1.lineTo(0.49449, -0.4373)
loop_1 = loop_1.lineTo(0.55736, -0.44136)
loop_1 = loop_1.lineTo(0.62018, -0.44013)
loop_1 = loop_1.lineTo(0.67939, -0.44281)
loop_1 = loop_1.lineTo(0.73224, -0.4437)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_41_interval_0.stl')