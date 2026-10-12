import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52664), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.42, -0.87382)
loop_1 = loop_1.lineTo(0.41935, -0.97984)
loop_1 = loop_1.lineTo(-0.00232, -0.97926)
loop_1 = loop_1.lineTo(0.0456, -0.97608)
loop_1 = loop_1.threePointArc((0.07472, -0.9729), (0.10232, -0.96953))
loop_1 = loop_1.lineTo(0.35147, -0.90482)
loop_1 = loop_1.threePointArc((0.3799, -0.89242), (0.40676, -0.88032))
loop_1 = loop_1.lineTo(0.42, -0.87382)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_86_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_86_interval_0.stl')