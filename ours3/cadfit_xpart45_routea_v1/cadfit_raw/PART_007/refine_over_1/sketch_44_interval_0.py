import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43245, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.05621, 0.55147)
loop_1 = loop_1.threePointArc((0.00688, 0.55091), (-0.04451, 0.55162))
loop_1 = loop_1.threePointArc((-0.08522, 0.55087), (-0.12688, 0.5516))
loop_1 = loop_1.threePointArc((-0.21137, 0.55031), (-0.29864, 0.55034))
loop_1 = loop_1.threePointArc((-0.34369, 0.54895), (-0.38989, 0.54963))
loop_1 = loop_1.threePointArc((-0.44385, 0.5484), (-0.49934, 0.54889))
loop_1 = loop_1.lineTo(-0.57103, 0.54807)
loop_1 = loop_1.lineTo(-0.71083, 0.54834)
loop_1 = loop_1.lineTo(-0.76897, 0.54811)
loop_1 = loop_1.threePointArc((-0.8128, 0.54734), (-0.85775, 0.54747))
loop_1 = loop_1.threePointArc((-0.88958, 0.54663), (-0.922, 0.54721))
loop_1 = loop_1.lineTo(-0.96178, 0.54347)
loop_1 = loop_1.lineTo(0.05551, 0.55159)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_44_interval_0.stl')