import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.16715, 0.03539, 0.18834), normal=(0.00053, 0.00185, -1.0), xDir=(0.0, -1.0, -0.00185))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.78694, 0.381)
loop_1 = loop_1.lineTo(0.78697, 0.31991)
loop_1 = loop_1.lineTo(0.75632, 0.34956)
loop_1 = loop_1.lineTo(0.74632, 0.36318)
loop_1 = loop_1.lineTo(0.73102, 0.381)
loop_1 = loop_1.lineTo(0.78598, 0.381)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.44)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_20_interval_0.stl')