import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.29007, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.99324, 0.17339)
loop_1 = loop_1.lineTo(-0.99239, 0.14978)
loop_1 = loop_1.lineTo(-0.98588, 0.09891)
loop_1 = loop_1.lineTo(-0.97173, 0.06371)
loop_1 = loop_1.lineTo(-0.96383, 0.0472)
loop_1 = loop_1.threePointArc((-0.95455, 0.03451), (-0.94558, 0.02263))
loop_1 = loop_1.lineTo(-0.92479, -0.00419)
loop_1 = loop_1.threePointArc((-0.92811, -0.03058), (-0.93109, -0.05573))
loop_1 = loop_1.threePointArc((-0.95279, -0.06986), (-0.97306, -0.08364))
loop_1 = loop_1.lineTo(-0.9908, -0.10787)
loop_1 = loop_1.lineTo(-0.99324, -0.12692)
loop_1 = loop_1.lineTo(-0.99324, 0.17317)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.59)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_67_interval_0.stl')