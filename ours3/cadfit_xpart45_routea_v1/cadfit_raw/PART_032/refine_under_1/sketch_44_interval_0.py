import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00794, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.8772, -0.18881)
loop_1 = loop_1.lineTo(0.7662, -0.18908)
loop_1 = loop_1.lineTo(0.79075, -0.21293)
loop_1 = loop_1.threePointArc((0.79734, -0.21388), (0.80359, -0.2147))
loop_1 = loop_1.lineTo(0.83761, -0.21833)
loop_1 = loop_1.lineTo(0.86187, -0.20104)
loop_1 = loop_1.lineTo(0.87714, -0.18886)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_44_interval_0.stl')