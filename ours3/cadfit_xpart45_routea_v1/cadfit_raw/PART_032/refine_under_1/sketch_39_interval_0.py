import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.70583, 0.11897, -0.07256), normal=(-1.0, 0.0, 0.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56959, -0.13139)
loop_1 = loop_1.lineTo(0.5748, -0.13153)
loop_1 = loop_1.lineTo(0.57479, -0.21764)
loop_1 = loop_1.lineTo(-0.56961, -0.21691)
loop_1 = loop_1.lineTo(-0.5696, -0.14317)
loop_1 = loop_1.lineTo(-0.56959, -0.13139)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_39_interval_0.stl')