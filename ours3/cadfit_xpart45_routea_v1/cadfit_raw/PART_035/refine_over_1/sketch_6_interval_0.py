import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.53187, 0.0771, -0.02347), normal=(0.67102, -0.74143, 0.00244), xDir=(-0.74143, -0.67103, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.1067, 0.31398)
loop_1 = loop_1.lineTo(0.10703, 0.22761)
loop_1 = loop_1.lineTo(0.13126, 0.23444)
loop_1 = loop_1.lineTo(0.14177, 0.24039)
loop_1 = loop_1.lineTo(0.15227, 0.25872)
loop_1 = loop_1.lineTo(0.15556, 0.27005)
loop_1 = loop_1.lineTo(0.16228, 0.28498)
loop_1 = loop_1.threePointArc((0.17696, 0.29593), (0.18942, 0.30315))
loop_1 = loop_1.threePointArc((0.19911, 0.30248), (0.20467, 0.30119))
loop_1 = loop_1.threePointArc((0.18213, 0.30694), (0.15743, 0.31234))
loop_1 = loop_1.threePointArc((0.13152, 0.31318), (0.10833, 0.31392))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_6_interval_0.stl')