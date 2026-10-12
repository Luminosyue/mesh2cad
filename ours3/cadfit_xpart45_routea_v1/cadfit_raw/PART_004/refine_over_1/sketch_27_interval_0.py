import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.30223, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.19135, 0.77407)
loop_1 = loop_1.lineTo(0.32771, 0.8)
loop_1 = loop_1.lineTo(0.14722, 0.79967)
loop_1 = loop_1.lineTo(0.15524, 0.78714)
loop_1 = loop_1.lineTo(0.17218, 0.77798)
loop_1 = loop_1.lineTo(0.20695, 0.76753)
loop_1 = loop_1.lineTo(0.21732, 0.76692)
loop_1 = loop_1.lineTo(0.24257, 0.76664)
loop_1 = loop_1.lineTo(0.19153, 0.77407)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.71)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_27_interval_0.stl')