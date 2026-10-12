import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.39348), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.01526, 0.60345)
loop_1 = loop_1.lineTo(0.97, 0.60083)
loop_1 = loop_1.lineTo(0.97, 0.58579)
loop_1 = loop_1.threePointArc((0.93622, 0.59573), (0.91319, 0.59689))
loop_1 = loop_1.lineTo(0.82177, 0.59747)
loop_1 = loop_1.threePointArc((0.67711, 0.6003), (0.53883, 0.60029))
loop_1 = loop_1.threePointArc((0.50222, 0.60092), (0.46771, 0.60006))
loop_1 = loop_1.threePointArc((0.42109, 0.6009), (0.37697, 0.60049))
loop_1 = loop_1.threePointArc((0.31353, 0.60162), (0.25328, 0.60103))
loop_1 = loop_1.lineTo(0.16907, 0.60177)
loop_1 = loop_1.lineTo(0.10382, 0.60249)
loop_1 = loop_1.threePointArc((0.06429, 0.60224), (0.02379, 0.60279))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_57_interval_0.stl')