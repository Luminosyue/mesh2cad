import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.8003, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02015, 0.21006)
loop_1 = loop_1.lineTo(-0.02049, 0.09655)
loop_1 = loop_1.threePointArc((-0.03063, 0.10846), (-0.04057, 0.11954))
loop_1 = loop_1.threePointArc((-0.05173, 0.13211), (-0.06248, 0.14397))
loop_1 = loop_1.lineTo(-0.09669, 0.17931)
loop_1 = loop_1.lineTo(-0.12835, 0.20869)
loop_1 = loop_1.lineTo(-0.02028, 0.21006)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_33_interval_0.stl')