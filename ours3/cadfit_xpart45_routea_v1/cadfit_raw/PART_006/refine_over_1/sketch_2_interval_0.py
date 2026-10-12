import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.47358, 0.76462, -0.06766), normal=(0.51795, 0.85541, 5e-05), xDir=(0.85541, -0.51795, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26504, 0.45298)
loop_1 = loop_1.lineTo(-0.3187, 0.45298)
loop_1 = loop_1.lineTo(-0.3186, 0.27075)
loop_1 = loop_1.lineTo(-0.31829, 0.28232)
loop_1 = loop_1.lineTo(-0.31258, 0.32945)
loop_1 = loop_1.threePointArc((-0.31217, 0.34337), (-0.3115, 0.35558))
loop_1 = loop_1.lineTo(-0.31029, 0.37949)
loop_1 = loop_1.lineTo(-0.30721, 0.39238)
loop_1 = loop_1.lineTo(-0.29204, 0.41589)
loop_1 = loop_1.lineTo(-0.28076, 0.44439)
loop_1 = loop_1.lineTo(-0.26996, 0.44964)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_2_interval_0.stl')