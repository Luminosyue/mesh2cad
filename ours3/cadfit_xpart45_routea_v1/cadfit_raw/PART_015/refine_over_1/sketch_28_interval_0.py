import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.67008, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.67239, -0.25215)
loop_1 = loop_1.lineTo(0.65184, -0.25717)
loop_1 = loop_1.lineTo(0.62049, -0.25988)
loop_1 = loop_1.threePointArc((0.58447, -0.25946), (0.54735, -0.25808))
loop_1 = loop_1.threePointArc((0.50539, -0.25746), (0.46547, -0.25752))
loop_1 = loop_1.lineTo(0.24198, -0.25847)
loop_1 = loop_1.threePointArc((0.20124, -0.25929), (0.15917, -0.25909))
loop_1 = loop_1.lineTo(0.14055, -0.25975)
loop_1 = loop_1.lineTo(0.12954, -0.26215)
loop_1 = loop_1.lineTo(0.67239, -0.26072)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_28_interval_0.stl')