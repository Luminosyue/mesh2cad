import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.12783, 0.17627, 0.13325), normal=(-0.00237, -0.99939, -0.03491), xDir=(-1.0, 0.00238, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.84632, -0.01214)
loop_1 = loop_1.lineTo(0.84694, 0.02227)
loop_1 = loop_1.lineTo(-0.49753, 0.02745)
loop_1 = loop_1.lineTo(-0.52958, 0.02949)
loop_1 = loop_1.lineTo(-0.62771, 0.02956)
loop_1 = loop_1.lineTo(-0.65963, 0.02959)
loop_1 = loop_1.lineTo(-0.86854, 0.02975)
loop_1 = loop_1.lineTo(-0.86802, -0.01459)
loop_1 = loop_1.lineTo(-0.85602, -0.02027)
loop_1 = loop_1.lineTo(0.84332, -0.01913)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_23_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_23_interval_0.stl')