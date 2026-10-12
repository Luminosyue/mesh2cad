import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.77, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.25981, 0.23363)
loop_1 = loop_1.lineTo(0.27068, 0.23178)
loop_1 = loop_1.lineTo(0.46883, 0.23236)
loop_1 = loop_1.lineTo(0.77925, 0.23034)
loop_1 = loop_1.lineTo(0.83032, 0.22878)
loop_1 = loop_1.lineTo(0.87158, 0.21016)
loop_1 = loop_1.lineTo(-0.85936, 0.21637)
loop_1 = loop_1.lineTo(-0.83415, 0.22679)
loop_1 = loop_1.threePointArc((-0.72975, 0.22995), (-0.62216, 0.23074))
loop_1 = loop_1.lineTo(-0.39702, 0.23231)
loop_1 = loop_1.threePointArc((-0.32701, 0.23252), (-0.26097, 0.23382))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.34)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_55_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_55_interval_0.stl')