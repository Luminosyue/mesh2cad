import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.62225, -0.79145, -0.15319), normal=(0.71469, 0.69945, 0.00019), xDir=(0.69945, -0.71469, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26513, 0.38425)
loop_1 = loop_1.lineTo(-0.27885, 0.36345)
loop_1 = loop_1.threePointArc((-0.28573, 0.34918), (-0.29251, 0.33541))
loop_1 = loop_1.threePointArc((-0.2944, 0.32722), (-0.29591, 0.32028))
loop_1 = loop_1.lineTo(-0.29945, 0.30439)
loop_1 = loop_1.lineTo(-0.29942, 0.39029)
loop_1 = loop_1.lineTo(-0.25753, 0.39029)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_53_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_53_interval_0.stl')