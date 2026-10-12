import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0584, 0.98186, -0.0474), normal=(-0.00029, -0.99999, -0.0052), xDir=(-1.0, 0.00029, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.27241, -0.22082)
loop_1 = loop_1.lineTo(0.30684, -0.22082)
loop_1 = loop_1.threePointArc((0.28078, -0.23175), (0.25961, -0.2405))
loop_1 = loop_1.lineTo(0.21935, -0.25081)
loop_1 = loop_1.lineTo(0.17343, -0.25867)
loop_1 = loop_1.lineTo(0.13147, -0.25981)
loop_1 = loop_1.lineTo(0.08795, -0.2618)
loop_1 = loop_1.lineTo(0.04506, -0.26622)
loop_1 = loop_1.lineTo(0.00074, -0.26409)
loop_1 = loop_1.lineTo(-0.04244, -0.26452)
loop_1 = loop_1.lineTo(-0.08561, -0.26736)
loop_1 = loop_1.lineTo(-0.12878, -0.26633)
loop_1 = loop_1.lineTo(-0.17085, -0.26321)
loop_1 = loop_1.lineTo(-0.18151, -0.25956)
loop_1 = loop_1.lineTo(-0.21539, -0.2515)
loop_1 = loop_1.lineTo(-0.25693, -0.2306)
loop_1 = loop_1.lineTo(-0.26771, -0.22367)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.84)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_8_interval_0.stl')