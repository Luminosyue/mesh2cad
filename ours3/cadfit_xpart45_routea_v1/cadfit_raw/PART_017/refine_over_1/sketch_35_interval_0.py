import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58687, -0.04406, 0.50806), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16894, -1.33599)
loop_1 = loop_1.threePointArc((0.17393, -1.34217), (0.17885, -1.34799))
loop_1 = loop_1.lineTo(0.20106, -1.37457)
loop_1 = loop_1.threePointArc((0.21457, -1.38632), (0.22176, -1.39147))
loop_1 = loop_1.lineTo(0.24589, -1.40869)
loop_1 = loop_1.threePointArc((0.26242, -1.41206), (0.27741, -1.41491))
loop_1 = loop_1.lineTo(0.17005, -1.33679)
loop_1 = loop_1.close()
loop_2 = sketch_1.moveTo(0.16894, -1.33599)
loop_2 = loop_2.threePointArc((0.17393, -1.34217), (0.17885, -1.34799))
loop_2 = loop_2.lineTo(0.20106, -1.37457)
loop_2 = loop_2.threePointArc((0.21457, -1.38632), (0.22176, -1.39147))
loop_2 = loop_2.lineTo(0.24589, -1.40869)
loop_2 = loop_2.threePointArc((0.26231, -1.41204), (0.2772, -1.41487))
loop_2 = loop_2.lineTo(0.17005, -1.33679)
loop_2 = loop_2.close()
sketch_1=sketch_1.add(loop_1).add(loop_2)
solid_1 = sketch_1.extrude(0.13)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_35_interval_0.stl')