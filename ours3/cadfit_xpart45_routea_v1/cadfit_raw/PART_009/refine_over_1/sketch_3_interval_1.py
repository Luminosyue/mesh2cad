import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.68559, 0.54442, 0.07579), normal=(0.79025, 0.61278, -0.00023), xDir=(0.61278, -0.79025, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.18246, 0.01147)
loop_1 = loop_1.lineTo(-0.20976, 0.00749)
loop_1 = loop_1.lineTo(-0.25478, 0.13106)
loop_1 = loop_1.lineTo(-0.25554, -0.00115)
loop_1 = loop_1.lineTo(-0.24501, 0.00274)
loop_1 = loop_1.lineTo(-0.23105, 0.00439)
loop_1 = loop_1.lineTo(-0.19936, 0.00193)
loop_1 = loop_1.lineTo(-0.18399, 0.0106)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_3_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_3_interval_1.stl')