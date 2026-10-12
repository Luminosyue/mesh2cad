import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01157, 0.22523, 0.34685), normal=(-0.0, -0.95602, 0.2933), xDir=(-1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.24207, -0.4057)
loop_1 = loop_1.lineTo(0.21069, -0.41072)
loop_1 = loop_1.lineTo(0.19982, -0.40936)
loop_1 = loop_1.lineTo(0.17067, -0.41487)
loop_1 = loop_1.lineTo(0.1595, -0.4153)
loop_1 = loop_1.lineTo(0.13805, -0.41824)
loop_1 = loop_1.lineTo(0.12745, -0.41994)
loop_1 = loop_1.lineTo(0.05698, -0.42352)
loop_1 = loop_1.lineTo(-0.01705, -0.42562)
loop_1 = loop_1.lineTo(0.26157, -0.42562)
loop_1 = loop_1.lineTo(0.26157, -0.40576)
loop_1 = loop_1.lineTo(0.24633, -0.40603)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_23_interval_0.stl')