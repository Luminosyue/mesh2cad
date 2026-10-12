import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8503, 0.27804, -0.03758), normal=(0.92728, -0.37435, 0.00299), xDir=(-0.37435, -0.92729, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28479, 0.21064)
loop_1 = loop_1.lineTo(0.24282, 0.2413)
loop_1 = loop_1.lineTo(0.31535, 0.23582)
loop_1 = loop_1.lineTo(0.29256, 0.21443)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_19_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_19_interval_0.stl')