import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.12245, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.97, -0.58449)
loop_1 = loop_1.lineTo(-0.95946, -0.59125)
loop_1 = loop_1.threePointArc((-0.93649, -0.59482), (-0.91429, -0.59708))
loop_1 = loop_1.lineTo(-0.67153, -0.60151)
loop_1 = loop_1.lineTo(-0.40263, -0.60387)
loop_1 = loop_1.lineTo(-0.2064, -0.60528)
loop_1 = loop_1.lineTo(-0.04903, -0.60604)
loop_1 = loop_1.lineTo(-0.97, -0.60393)
loop_1 = loop_1.lineTo(-0.97, -0.58511)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_43_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_43_interval_0.stl')