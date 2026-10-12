import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.32118, 0.24205, 0.08269), normal=(0.01343, -0.129, -0.99155), xDir=(0.0, -0.99164, 0.12901))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.55914, 1.04666)
loop_1 = loop_1.lineTo(-0.57104, 1.03104)
loop_1 = loop_1.lineTo(-0.58243, 1.01216)
loop_1 = loop_1.lineTo(-0.59312, 0.99239)
loop_1 = loop_1.lineTo(-0.59876, 0.98219)
loop_1 = loop_1.lineTo(-0.61565, 0.95081)
loop_1 = loop_1.threePointArc((-0.60857, 0.96373), (-0.60333, 0.97328))
loop_1 = loop_1.lineTo(-0.47246, 1.10144)
loop_1 = loop_1.threePointArc((-0.48364, 1.09699), (-0.49247, 1.09344))
loop_1 = loop_1.lineTo(-0.50437, 1.08743)
loop_1 = loop_1.lineTo(-0.53456, 1.07085)
loop_1 = loop_1.lineTo(-0.55174, 1.05453)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_19_interval_0.stl')