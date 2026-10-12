import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29195, 0.85359, -0.01196), normal=(-0.37552, 0.92681, 0.00012), xDir=(0.92681, 0.37552, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35994, 0.50868)
loop_1 = loop_1.lineTo(-0.30776, 0.50868)
loop_1 = loop_1.lineTo(-0.32166, 0.49684)
loop_1 = loop_1.lineTo(-0.33647, 0.46119)
loop_1 = loop_1.lineTo(-0.3429, 0.44807)
loop_1 = loop_1.lineTo(-0.34513, 0.42046)
loop_1 = loop_1.threePointArc((-0.34924, 0.38507), (-0.35169, 0.35434))
loop_1 = loop_1.lineTo(-0.35249, 0.3406)
loop_1 = loop_1.threePointArc((-0.35197, 0.31583), (-0.35115, 0.29206))
loop_1 = loop_1.lineTo(-0.35477, 0.23674)
loop_1 = loop_1.lineTo(-0.35632, 0.22329)
loop_1 = loop_1.lineTo(-0.36005, 0.19947)
loop_1 = loop_1.lineTo(-0.35994, 0.50524)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_8_interval_0.stl')