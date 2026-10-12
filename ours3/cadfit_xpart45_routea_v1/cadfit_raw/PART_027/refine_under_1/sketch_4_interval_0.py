import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45927, 0.27402, -0.07227), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03328, -0.6197)
loop_1 = loop_1.lineTo(-0.0295, -0.62983)
loop_1 = loop_1.lineTo(0.00503, -0.68149)
loop_1 = loop_1.lineTo(0.04409, -0.7137)
loop_1 = loop_1.lineTo(0.06362, -0.7227)
loop_1 = loop_1.lineTo(0.08315, -0.72431)
loop_1 = loop_1.lineTo(0.09569, -0.7207)
loop_1 = loop_1.lineTo(0.11378, -0.7137)
loop_1 = loop_1.lineTo(0.12638, -0.69417)
loop_1 = loop_1.lineTo(0.12467, -0.67464)
loop_1 = loop_1.lineTo(0.11716, -0.65511)
loop_1 = loop_1.lineTo(0.10798, -0.64088)
loop_1 = loop_1.lineTo(0.09273, -0.62449)
loop_1 = loop_1.lineTo(0.00266, -0.59118)
loop_1 = loop_1.lineTo(-0.00919, -0.59308)
loop_1 = loop_1.lineTo(-0.02384, -0.59854)
loop_1 = loop_1.lineTo(-0.03404, -0.6147)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_4_interval_0.stl')