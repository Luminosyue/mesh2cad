import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0269, -0.85761, -0.02077), normal=(-0.00198, 1.0, 0.00018), xDir=(1.0, 0.00198, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3322, 0.27714)
loop_1 = loop_1.lineTo(0.28882, 0.27714)
loop_1 = loop_1.lineTo(0.2887, -0.12862)
loop_1 = loop_1.lineTo(-0.33221, -0.12862)
loop_1 = loop_1.lineTo(-0.3322, 0.26508)
loop_1 = loop_1.lineTo(-0.3322, 0.27714)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_36_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_36_interval_0.stl')