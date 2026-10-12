import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.40223, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08328, 0.8)
loop_1 = loop_1.lineTo(-0.18773, 0.79977)
loop_1 = loop_1.lineTo(-0.17738, 0.78828)
loop_1 = loop_1.lineTo(-0.14222, 0.7719)
loop_1 = loop_1.lineTo(-0.10767, 0.77926)
loop_1 = loop_1.lineTo(-0.08714, 0.79025)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.79)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_28_interval_0.stl')