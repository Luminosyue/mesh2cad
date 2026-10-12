import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.94582, 0.0864)
loop_1 = loop_1.lineTo(0.91878, 0.04884)
loop_1 = loop_1.threePointArc((0.90684, 0.03767), (0.89564, 0.02684))
loop_1 = loop_1.lineTo(0.86509, -0.0027)
loop_1 = loop_1.lineTo(0.89623, -0.0546)
loop_1 = loop_1.lineTo(0.90643, -0.05886)
loop_1 = loop_1.lineTo(0.9455, -0.08579)
loop_1 = loop_1.lineTo(0.94582, 0.08638)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_50_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_50_interval_0.stl')