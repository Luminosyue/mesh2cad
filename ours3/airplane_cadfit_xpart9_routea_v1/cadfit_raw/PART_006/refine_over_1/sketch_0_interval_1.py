import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.722, 0.05063, 0.00818), normal=(0.97878, 0.18685, -0.08409), xDir=(0.18752, -0.98226, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27045, 0.14348)
loop_1 = loop_1.lineTo(-0.28087, 0.05303)
loop_1 = loop_1.lineTo(0.14929, 0.005)
loop_1 = loop_1.lineTo(0.15499, 0.03358)
loop_1 = loop_1.lineTo(-0.26581, 0.14228)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.67)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_0_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_0_interval_1.stl')