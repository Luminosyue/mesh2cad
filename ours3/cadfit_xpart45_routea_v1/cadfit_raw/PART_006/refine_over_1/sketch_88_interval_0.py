import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.52029), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.15284, 0.96662)
loop_1 = loop_1.lineTo(0.11844, 0.97501)
loop_1 = loop_1.threePointArc((0.09165, 0.97961), (0.06615, 0.98357))
loop_1 = loop_1.threePointArc((0.05586, 0.98426), (0.04551, 0.98551))
loop_1 = loop_1.lineTo(0.01153, 0.9881)
loop_1 = loop_1.lineTo(0.39, 0.98724)
loop_1 = loop_1.lineTo(0.38951, 0.88266)
loop_1 = loop_1.threePointArc((0.37732, 0.88958), (0.36539, 0.89518))
loop_1 = loop_1.threePointArc((0.34574, 0.90447), (0.32692, 0.91279))
loop_1 = loop_1.threePointArc((0.2841, 0.9271), (0.24305, 0.94007))
loop_1 = loop_1.threePointArc((0.22063, 0.94688), (0.19771, 0.9543))
loop_1 = loop_1.lineTo(0.17021, 0.9624)
loop_1 = loop_1.lineTo(0.15284, 0.96662)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.05)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_88_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_88_interval_0.stl')