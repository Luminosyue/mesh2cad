import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72222, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.67652, -0.2727)
loop_1 = loop_1.lineTo(0.80492, -0.2903)
loop_1 = loop_1.lineTo(0.79234, -0.29877)
loop_1 = loop_1.lineTo(0.76301, -0.30841)
loop_1 = loop_1.lineTo(0.7443, -0.31732)
loop_1 = loop_1.threePointArc((0.7168, -0.31916), (0.69147, -0.32214))
loop_1 = loop_1.lineTo(0.57467, -0.32254)
loop_1 = loop_1.lineTo(0.40965, -0.32046)
loop_1 = loop_1.threePointArc((0.24456, -0.3208), (0.08705, -0.32249))
loop_1 = loop_1.threePointArc((-0.01577, -0.3215), (-0.12182, -0.31958))
loop_1 = loop_1.lineTo(-0.2758, -0.31949)
loop_1 = loop_1.lineTo(-0.43076, -0.31532)
loop_1 = loop_1.lineTo(-0.60435, -0.30612)
loop_1 = loop_1.threePointArc((-0.63138, -0.30008), (-0.65768, -0.29101))
loop_1 = loop_1.threePointArc((-0.66359, -0.28726), (-0.66844, -0.28345))
loop_1 = loop_1.lineTo(-0.67652, -0.2727)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.43)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_51_interval_0.stl')