import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.02925), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05543, 0.88146)
loop_1 = loop_1.lineTo(-0.25903, -0.08986)
loop_1 = loop_1.threePointArc((-0.25393, -0.02889), (-0.24373, 0.03325))
loop_1 = loop_1.threePointArc((-0.23925, 0.07058), (-0.23257, 0.10835))
loop_1 = loop_1.threePointArc((-0.22648, 0.16327), (-0.21676, 0.21914))
loop_1 = loop_1.threePointArc((-0.20538, 0.26526), (-0.19267, 0.31226))
loop_1 = loop_1.threePointArc((-0.17972, 0.3815), (-0.16896, 0.44751))
loop_1 = loop_1.threePointArc((-0.15563, 0.51857), (-0.14585, 0.58654))
loop_1 = loop_1.threePointArc((-0.14027, 0.63023), (-0.1328, 0.67471))
loop_1 = loop_1.lineTo(-0.11926, 0.77806)
loop_1 = loop_1.threePointArc((-0.11494, 0.79476), (-0.10964, 0.81117))
loop_1 = loop_1.lineTo(-0.10926, 0.91116)
loop_1 = loop_1.lineTo(-0.00249, 0.91025)
loop_1 = loop_1.threePointArc((-0.01311, 0.90511), (-0.02169, 0.89887))
loop_1 = loop_1.lineTo(-0.04897, 0.88707)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_59_interval_0.stl')