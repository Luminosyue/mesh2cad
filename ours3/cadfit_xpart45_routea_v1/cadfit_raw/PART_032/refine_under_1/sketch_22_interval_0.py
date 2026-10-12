import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07603, 0.94475, -0.0688), normal=(4e-05, -0.99993, 0.01141), xDir=(-1.0, -4e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.26297, -0.16836)
loop_1 = loop_1.lineTo(-0.35326, -0.16836)
loop_1 = loop_1.lineTo(-0.36324, 0.19166)
loop_1 = loop_1.lineTo(0.27315, 0.19166)
loop_1 = loop_1.lineTo(0.26324, -0.15891)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.64)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_22_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_22_interval_0.stl')