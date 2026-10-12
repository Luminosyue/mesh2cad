import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.03434, 0.2783, -0.21556), normal=(0.01246, -0.99992, -0.00166), xDir=(-0.99992, -0.01246, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29062, -0.73394)
loop_1 = loop_1.lineTo(-0.29599, -0.99638)
loop_1 = loop_1.lineTo(-0.29426, -1.03129)
loop_1 = loop_1.lineTo(-0.29083, -1.06607)
loop_1 = loop_1.lineTo(-0.29029, -1.04882)
loop_1 = loop_1.lineTo(-0.28482, -1.06769)
loop_1 = loop_1.lineTo(-0.26687, -1.09596)
loop_1 = loop_1.threePointArc((-0.25904, -1.10336), (-0.25511, -1.10576))
loop_1 = loop_1.lineTo(-0.29045, -0.74763)
loop_1 = loop_1.lineTo(-0.29062, -0.73394)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_16_interval_0.stl')