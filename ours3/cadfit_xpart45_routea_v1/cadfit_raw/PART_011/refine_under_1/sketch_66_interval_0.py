import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.25417), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.78817, 0.51487)
loop_1 = loop_1.lineTo(0.73147, 0.51836)
loop_1 = loop_1.threePointArc((0.66258, 0.60208), (0.5892, 0.67436))
loop_1 = loop_1.threePointArc((0.54346, 0.71136), (0.49921, 0.74471))
loop_1 = loop_1.threePointArc((0.46282, 0.7662), (0.42826, 0.78531))
loop_1 = loop_1.threePointArc((0.31777, 0.83945), (0.20753, 0.8789))
loop_1 = loop_1.threePointArc((0.16622, 0.88691), (0.12729, 0.89203))
loop_1 = loop_1.lineTo(0.00588, 0.907)
loop_1 = loop_1.threePointArc((-0.02139, 0.90895), (-0.04654, 0.90755))
loop_1 = loop_1.threePointArc((-0.08454, 0.90522), (-0.11974, 0.90076))
loop_1 = loop_1.threePointArc((-0.19366, 0.89349), (-0.26279, 0.88127))
loop_1 = loop_1.threePointArc((-0.36496, 0.84356), (-0.45996, 0.80256))
loop_1 = loop_1.threePointArc((-0.5034, 0.77812), (-0.54252, 0.75248))
loop_1 = loop_1.threePointArc((-0.65432, 0.65973), (-0.75182, 0.56142))
loop_1 = loop_1.threePointArc((-0.7704, 0.53769), (-0.78745, 0.51569))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_66_interval_0.stl')