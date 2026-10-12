import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.44412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.32457, 0.73941)
loop_1 = loop_1.threePointArc((0.32322, 0.74191), (0.31776, 0.75213))
loop_1 = loop_1.lineTo(0.30667, 0.77)
loop_1 = loop_1.lineTo(0.37571, 0.76984)
loop_1 = loop_1.lineTo(0.32462, 0.73944)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_66_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_66_interval_0.stl')