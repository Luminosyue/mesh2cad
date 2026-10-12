import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8503, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.23491, 0.18582)
loop_1 = loop_1.lineTo(-0.24246, 0.14591)
loop_1 = loop_1.lineTo(-0.23485, 0.1235)
loop_1 = loop_1.lineTo(-0.22678, 0.10665)
loop_1 = loop_1.lineTo(-0.205, 0.07161)
loop_1 = loop_1.threePointArc((-0.20078, 0.06533), (-0.19665, 0.05876))
loop_1 = loop_1.lineTo(-0.18584, 0.04239)
loop_1 = loop_1.lineTo(-0.28562, 0.11643)
loop_1 = loop_1.lineTo(-0.23495, 0.1857)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.93)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_34_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_34_interval_0.stl')