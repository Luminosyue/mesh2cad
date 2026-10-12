import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.01229, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77439, -0.03462)
loop_1 = loop_1.threePointArc((-0.76736, -0.03788), (-0.76022, -0.04163))
loop_1 = loop_1.lineTo(-0.67835, -0.11623)
loop_1 = loop_1.lineTo(-0.58232, -0.0836)
loop_1 = loop_1.lineTo(-0.61222, -0.08299)
loop_1 = loop_1.threePointArc((-0.6226, -0.08243), (-0.6324, -0.08221))
loop_1 = loop_1.lineTo(-0.64462, -0.08055)
loop_1 = loop_1.threePointArc((-0.66397, -0.07795), (-0.67413, -0.07632))
loop_1 = loop_1.threePointArc((-0.6849, -0.07262), (-0.69521, -0.06959))
loop_1 = loop_1.threePointArc((-0.70576, -0.06533), (-0.71592, -0.06186))
loop_1 = loop_1.lineTo(-0.73142, -0.05507)
loop_1 = loop_1.threePointArc((-0.73864, -0.05198), (-0.74583, -0.0485))
loop_1 = loop_1.threePointArc((-0.75758, -0.04291), (-0.76943, -0.03671))
loop_1 = loop_1.lineTo(-0.80617, -0.0099)
loop_1 = loop_1.lineTo(-0.77918, -0.03332)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_27_interval_0.stl')