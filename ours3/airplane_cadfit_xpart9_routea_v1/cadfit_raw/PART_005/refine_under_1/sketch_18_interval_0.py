import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03322, 0.10299, -0.03161), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4169, 0.0329)
loop_1 = loop_1.lineTo(-0.43274, 0.02635)
loop_1 = loop_1.threePointArc((-0.44798, 0.0194), (-0.45645, 0.01604))
loop_1 = loop_1.lineTo(-0.49271, -0.00166)
loop_1 = loop_1.lineTo(-0.50704, -0.00782)
loop_1 = loop_1.threePointArc((-0.52861, -0.01634), (-0.54399, -0.02355))
loop_1 = loop_1.threePointArc((-0.55118, -0.02791), (-0.55763, -0.03089))
loop_1 = loop_1.lineTo(0.14434, -0.03109)
loop_1 = loop_1.lineTo(0.14434, 0.02322)
loop_1 = loop_1.lineTo(-0.4164, 0.02368)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_18_interval_0.stl')