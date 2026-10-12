import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.33573, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.98734, -0.49905)
loop_1 = loop_1.lineTo(-0.77783, -0.50175)
loop_1 = loop_1.threePointArc((-0.79818, -0.50715), (-0.81554, -0.51139))
loop_1 = loop_1.threePointArc((-0.82829, -0.51383), (-0.84026, -0.51664))
loop_1 = loop_1.threePointArc((-0.84754, -0.51766), (-0.85432, -0.51886))
loop_1 = loop_1.lineTo(-0.8664, -0.52131)
loop_1 = loop_1.lineTo(-0.87864, -0.52278)
loop_1 = loop_1.lineTo(-0.89201, -0.52554)
loop_1 = loop_1.lineTo(-0.93613, -0.5299)
loop_1 = loop_1.threePointArc((-0.94569, -0.53059), (-0.95549, -0.53104))
loop_1 = loop_1.threePointArc((-0.96151, -0.53206), (-0.96706, -0.53329))
loop_1 = loop_1.lineTo(-0.98006, -0.53573)
loop_1 = loop_1.lineTo(-0.98838, -0.54811)
loop_1 = loop_1.lineTo(-0.99262, -0.53504)
loop_1 = loop_1.lineTo(-0.98724, -0.50197)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.14)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_46_interval_0.stl')