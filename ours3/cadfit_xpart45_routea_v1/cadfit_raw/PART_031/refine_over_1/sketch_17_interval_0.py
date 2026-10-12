import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.04389, -0.66457, 0.25093), normal=(-1e-05, 0.71702, 0.69705), xDir=(1.0, 1e-05, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.86002, 0.47272)
loop_1 = loop_1.threePointArc((-0.86779, 0.45793), (-0.87523, 0.44372))
loop_1 = loop_1.lineTo(-0.88049, 0.4284)
loop_1 = loop_1.threePointArc((-0.87967, 0.40929), (-0.87916, 0.38936))
loop_1 = loop_1.threePointArc((-0.87848, 0.37439), (-0.87806, 0.3628))
loop_1 = loop_1.threePointArc((-0.8749, 0.34068), (-0.87268, 0.32178))
loop_1 = loop_1.lineTo(-0.87016, 0.3027)
loop_1 = loop_1.threePointArc((-0.86841, 0.28536), (-0.86734, 0.27215))
loop_1 = loop_1.lineTo(-0.86449, 0.25034)
loop_1 = loop_1.lineTo(-0.85215, 0.18452)
loop_1 = loop_1.threePointArc((-0.84308, 0.15457), (-0.83532, 0.13131))
loop_1 = loop_1.threePointArc((-0.82492, 0.09536), (-0.8144, 0.06518))
loop_1 = loop_1.lineTo(-0.85954, 0.46857)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.6)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_17_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_17_interval_0.stl')