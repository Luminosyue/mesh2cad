import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.23114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.98271, 0.52021)
loop_1 = loop_1.lineTo(0.95964, -0.09699)
loop_1 = loop_1.lineTo(0.97864, -0.16098)
loop_1 = loop_1.threePointArc((0.98074, -0.22135), (0.98241, -0.28371))
loop_1 = loop_1.lineTo(0.98271, 0.51966)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_49_interval_0.stl')