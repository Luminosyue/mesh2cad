import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.95101, 0.05333, 0.10446), normal=(0.99988, -0.0084, -0.0128), xDir=(-0.0084, -0.99996, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29075, 0.07661)
loop_1 = loop_1.lineTo(-0.51682, 0.07661)
loop_1 = loop_1.lineTo(-0.517, 0.17662)
loop_1 = loop_1.lineTo(-0.46694, 0.15212)
loop_1 = loop_1.threePointArc((-0.44316, 0.141), (-0.4201, 0.12932))
loop_1 = loop_1.threePointArc((-0.37594, 0.10854), (-0.33623, 0.09276))
loop_1 = loop_1.threePointArc((-0.32138, 0.08758), (-0.31048, 0.08409))
loop_1 = loop_1.threePointArc((-0.28387, 0.07417), (-0.26117, 0.06655))
loop_1 = loop_1.lineTo(-0.02859, -0.01399)
loop_1 = loop_1.threePointArc((-0.04605, -0.00823), (-0.05971, -0.00321))
loop_1 = loop_1.threePointArc((-0.09032, 0.00657), (-0.12053, 0.01721))
loop_1 = loop_1.lineTo(-0.16172, 0.03041)
loop_1 = loop_1.lineTo(-0.19141, 0.04043)
loop_1 = loop_1.lineTo(-0.20817, 0.04625)
loop_1 = loop_1.threePointArc((-0.23973, 0.0578), (-0.27076, 0.06954))
loop_1 = loop_1.lineTo(-0.28987, 0.07629)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.93)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_0_interval_0.stl')