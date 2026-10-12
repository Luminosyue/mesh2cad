import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.19272, 0.86527, 0.02781), normal=(-0.2984, 0.95431, 0.01563), xDir=(0.95443, 0.29843, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.05712, 0.16924)
loop_1 = loop_1.lineTo(-0.06066, 0.13244)
loop_1 = loop_1.lineTo(-0.06198, 0.08392)
loop_1 = loop_1.threePointArc((-0.06475, 0.04268), (-0.06764, 0.0016))
loop_1 = loop_1.lineTo(-0.0697, 0.16845)
loop_1 = loop_1.lineTo(-0.05678, 0.17276)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_3_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_3_interval_0.stl')