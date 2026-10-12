import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.14265, -0.1247, -0.93116), normal=(0.05995, 0.00015, -0.9982), xDir=(0.0, -1.0, -0.00015))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.0953, 0.42241)
loop_1 = loop_1.lineTo(0.00614, 0.20415)
loop_1 = loop_1.threePointArc((0.01128, 0.1626), (0.01646, 0.12713))
loop_1 = loop_1.lineTo(0.02174, 0.07023)
loop_1 = loop_1.lineTo(0.02451, 0.04066)
loop_1 = loop_1.threePointArc((0.02508, 0.02042), (0.02516, 0.00358))
loop_1 = loop_1.lineTo(0.02745, -0.03858)
loop_1 = loop_1.threePointArc((0.03418, -0.08109), (0.04002, -0.11696))
loop_1 = loop_1.lineTo(0.04471, -0.15104)
loop_1 = loop_1.lineTo(0.04712, -0.18184)
loop_1 = loop_1.lineTo(0.04316, -0.20364)
loop_1 = loop_1.lineTo(0.03999, -0.21892)
loop_1 = loop_1.lineTo(0.01864, -0.25601)
loop_1 = loop_1.lineTo(0.00874, -0.27016)
loop_1 = loop_1.lineTo(0.0953, -0.27014)
loop_1 = loop_1.lineTo(0.0953, 0.41839)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_40_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_40_interval_1.stl')