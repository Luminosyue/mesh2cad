import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.83, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07436, 0.24147)
loop_1 = loop_1.lineTo(-0.17143, 0.23992)
loop_1 = loop_1.lineTo(-0.31661, 0.23797)
loop_1 = loop_1.threePointArc((-0.37624, 0.23642), (-0.43263, 0.23387))
loop_1 = loop_1.lineTo(-0.51075, 0.23188)
loop_1 = loop_1.lineTo(-0.5941, 0.22874)
loop_1 = loop_1.lineTo(-0.61465, 0.22227)
loop_1 = loop_1.lineTo(-0.64218, 0.21999)
loop_1 = loop_1.lineTo(0.64137, 0.21796)
loop_1 = loop_1.threePointArc((0.62442, 0.2243), (0.60855, 0.22888))
loop_1 = loop_1.threePointArc((0.55107, 0.23117), (0.49673, 0.23185))
loop_1 = loop_1.threePointArc((0.43027, 0.23402), (0.36199, 0.23684))
loop_1 = loop_1.lineTo(0.2502, 0.23812)
loop_1 = loop_1.threePointArc((0.15956, 0.23942), (0.07338, 0.2393))
loop_1 = loop_1.lineTo(-0.07351, 0.24147)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.53)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_57_interval_0.stl')