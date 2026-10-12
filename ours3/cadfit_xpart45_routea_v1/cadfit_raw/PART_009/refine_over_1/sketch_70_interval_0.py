import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.56603, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.83609, -0.07162)
loop_1 = loop_1.lineTo(-0.79962, -0.05566)
loop_1 = loop_1.lineTo(-0.79141, -0.03857)
loop_1 = loop_1.lineTo(-0.78421, -0.00789)
loop_1 = loop_1.lineTo(-0.78963, 0.00223)
loop_1 = loop_1.lineTo(-0.83681, 0.0441)
loop_1 = loop_1.lineTo(-0.84823, 0.06517)
loop_1 = loop_1.lineTo(-0.86288, 0.10296)
loop_1 = loop_1.lineTo(-0.84685, -0.00208)
loop_1 = loop_1.lineTo(-0.84044, 0.02412)
loop_1 = loop_1.lineTo(-0.84027, -0.0454)
loop_1 = loop_1.lineTo(-0.83612, -0.07145)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_70_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_70_interval_0.stl')