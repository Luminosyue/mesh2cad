import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.84303, 0.19772, -0.0896), normal=(0.99238, -0.12323, -0.00013), xDir=(-0.12323, -0.99238, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.00249, 0.24952)
loop_1 = loop_1.lineTo(0.02275, 0.24931)
loop_1 = loop_1.threePointArc((0.05376, 0.24923), (0.08041, 0.24837))
loop_1 = loop_1.lineTo(0.10003, 0.24774)
loop_1 = loop_1.threePointArc((0.1457, 0.24269), (0.18802, 0.23698))
loop_1 = loop_1.lineTo(0.23258, 0.22427)
loop_1 = loop_1.lineTo(0.25992, 0.21537)
loop_1 = loop_1.lineTo(-0.25651, 0.21506)
loop_1 = loop_1.lineTo(-0.23372, 0.22573)
loop_1 = loop_1.lineTo(-0.19242, 0.2389)
loop_1 = loop_1.lineTo(-0.18087, 0.2409)
loop_1 = loop_1.lineTo(-0.15959, 0.24241)
loop_1 = loop_1.lineTo(-0.13989, 0.24618)
loop_1 = loop_1.threePointArc((-0.09741, 0.24827), (-0.0609, 0.24867))
loop_1 = loop_1.lineTo(-0.04475, 0.24902)
loop_1 = loop_1.lineTo(-0.00256, 0.24943)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_42_interval_0.stl')