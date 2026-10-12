import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29195, 0.85359, -0.01196), normal=(-0.37552, 0.92681, 0.00012), xDir=(0.92681, 0.37552, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30625, -0.34008)
loop_1 = loop_1.lineTo(0.30631, -0.54132)
loop_1 = loop_1.lineTo(0.2651, -0.54132)
loop_1 = loop_1.lineTo(0.28307, -0.5143)
loop_1 = loop_1.lineTo(0.30116, -0.48805)
loop_1 = loop_1.lineTo(0.30122, -0.47682)
loop_1 = loop_1.threePointArc((0.3024, -0.45124), (0.30335, -0.42668))
loop_1 = loop_1.lineTo(0.3046, -0.38404)
loop_1 = loop_1.lineTo(0.30615, -0.34228)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_38_interval_2.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_38_interval_2.stl')