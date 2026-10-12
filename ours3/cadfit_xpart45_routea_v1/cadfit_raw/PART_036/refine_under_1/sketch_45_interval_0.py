import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.77228, -0.01923, -0.1875), normal=(-0.00766, -0.00229, 0.99997), xDir=(-0.0, 1.0, 0.00229))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00698, 1.7367)
loop_1 = loop_1.lineTo(-0.00318, 1.70066)
loop_1 = loop_1.lineTo(0.00343, 1.59817)
loop_1 = loop_1.lineTo(0.00517, 1.56749)
loop_1 = loop_1.threePointArc((0.00667, 1.54553), (0.00818, 1.52848))
loop_1 = loop_1.lineTo(0.00939, 1.50578)
loop_1 = loop_1.lineTo(0.01341, 1.44874)
loop_1 = loop_1.lineTo(0.01948, 1.36685)
loop_1 = loop_1.threePointArc((0.02038, 1.33951), (0.02017, 1.31604))
loop_1 = loop_1.threePointArc((0.01997, 1.27875), (0.02044, 1.2462))
loop_1 = loop_1.threePointArc((0.02022, 1.22023), (0.01975, 1.19744))
loop_1 = loop_1.lineTo(0.02085, 1.18001)
loop_1 = loop_1.lineTo(0.02414, 1.16732)
loop_1 = loop_1.threePointArc((0.02786, 1.15713), (0.03186, 1.14751))
loop_1 = loop_1.lineTo(0.00168, 1.70356)
loop_1 = loop_1.lineTo(-0.00109, 1.75476)
loop_1 = loop_1.lineTo(-0.00698, 1.7367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_45_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_45_interval_0.stl')