import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.38, 0.008, 0.07767), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00032, 1.06494)
loop_1 = loop_1.lineTo(0.01293, 1.06541)
loop_1 = loop_1.lineTo(-0.012, 1.06541)
loop_1 = loop_1.lineTo(-0.04624, 1.05342)
loop_1 = loop_1.lineTo(-0.08326, 1.03368)
loop_1 = loop_1.lineTo(-0.12028, 1.00955)
loop_1 = loop_1.lineTo(-0.16008, 0.98064)
loop_1 = loop_1.lineTo(-0.19431, 0.95015)
loop_1 = loop_1.lineTo(-0.23319, 0.8922)
loop_1 = loop_1.threePointArc((-0.24266, 0.87821), (-0.25071, 0.86659))
loop_1 = loop_1.lineTo(-0.00923, 1.06462)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.76)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_16_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_16_interval_0.stl')