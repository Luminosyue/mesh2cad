import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.07603, 0.95475, -0.06892), normal=(4e-05, -0.99993, 0.01141), xDir=(-1.0, -4e-05, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.14619, -0.21382)
loop_1 = loop_1.lineTo(-0.26814, -0.2137)
loop_1 = loop_1.lineTo(-0.27146, -0.12737)
loop_1 = loop_1.lineTo(0.15045, -0.1274)
loop_1 = loop_1.lineTo(0.14645, -0.20842)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.65)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_11_interval_0.stl')