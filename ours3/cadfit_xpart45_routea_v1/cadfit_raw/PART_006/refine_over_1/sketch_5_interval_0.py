import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.08312, 0.90314, 0.05097), normal=(0.17075, 0.98531, 0.00011), xDir=(0.98531, -0.17075, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20146, 0.57161)
loop_1 = loop_1.lineTo(-0.24119, 0.57161)
loop_1 = loop_1.lineTo(-0.2411, 0.39512)
loop_1 = loop_1.lineTo(-0.24019, 0.40886)
loop_1 = loop_1.lineTo(-0.23325, 0.46617)
loop_1 = loop_1.lineTo(-0.22707, 0.51101)
loop_1 = loop_1.lineTo(-0.21652, 0.54752)
loop_1 = loop_1.lineTo(-0.21241, 0.56301)
loop_1 = loop_1.lineTo(-0.20146, 0.57161)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_5_interval_0.stl')