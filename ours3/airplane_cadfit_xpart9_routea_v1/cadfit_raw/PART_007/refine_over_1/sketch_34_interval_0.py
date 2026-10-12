import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.10742), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.18935, 0.97719)
loop_1 = loop_1.lineTo(0.21358, 0.91005)
loop_1 = loop_1.lineTo(0.21783, 0.89684)
loop_1 = loop_1.lineTo(0.20196, 0.89357)
loop_1 = loop_1.lineTo(0.18935, 0.97712)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_34_interval_0.stl')