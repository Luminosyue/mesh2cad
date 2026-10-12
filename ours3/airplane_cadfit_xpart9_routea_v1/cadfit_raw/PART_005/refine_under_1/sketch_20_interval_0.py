import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03584, 0.17021, -0.14), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.42181, 0.03554)
loop_1 = loop_1.lineTo(0.45801, 0.0273)
loop_1 = loop_1.lineTo(0.47481, 0.02402)
loop_1 = loop_1.threePointArc((0.50361, 0.01851), (0.52518, 0.01365))
loop_1 = loop_1.lineTo(0.54171, 0.00894)
loop_1 = loop_1.threePointArc((0.55686, 0.00547), (0.57243, 0.00102))
loop_1 = loop_1.lineTo(0.58438, -0.00266)
loop_1 = loop_1.lineTo(0.60681, -0.00965)
loop_1 = loop_1.threePointArc((0.6206, -0.01408), (0.63486, -0.01901))
loop_1 = loop_1.lineTo(0.6459, -0.02206)
loop_1 = loop_1.threePointArc((0.65509, -0.02543), (0.66398, -0.02846))
loop_1 = loop_1.lineTo(-0.2086, -0.02847)
loop_1 = loop_1.lineTo(-0.2086, 0.02584)
loop_1 = loop_1.lineTo(0.42125, 0.02631)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/refine_under_1/sketch_20_interval_0.stl')