import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.00559, -0.05532, 0.96341), normal=(-0.00316, 0.00117, -0.99999), xDir=(0.0, -1.0, -0.00117))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.77765, 0.32479)
loop_1 = loop_1.lineTo(-0.77764, -0.31204)
loop_1 = loop_1.lineTo(0.67236, -0.3108)
loop_1 = loop_1.lineTo(0.67236, 0.32602)
loop_1 = loop_1.lineTo(-0.75645, 0.32481)
loop_1 = loop_1.lineTo(-0.77765, 0.32479)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.08)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_56_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_56_interval_0.stl')