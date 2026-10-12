import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.60232, -0.05985, 0.32), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.03164, 0.03007)
loop_1 = loop_1.threePointArc((-1.04253, 0.02077), (-1.05395, 0.01118))
loop_1 = loop_1.threePointArc((-1.04904, -0.01037), (-1.04304, -0.029))
loop_1 = loop_1.lineTo(-1.02535, -0.04032)
loop_1 = loop_1.lineTo(-0.98812, -0.03169)
loop_1 = loop_1.lineTo(0.92613, -0.10285)
loop_1 = loop_1.lineTo(0.92443, -0.03669)
loop_1 = loop_1.threePointArc((0.92144, -0.01701), (0.91706, 0.00014))
loop_1 = loop_1.threePointArc((0.90985, 0.01821), (0.9, 0.0254))
loop_1 = loop_1.lineTo(0.88866, 0.03225)
loop_1 = loop_1.lineTo(0.8651, 0.04597)
loop_1 = loop_1.threePointArc((0.64362, 0.04572), (0.41678, 0.04756))
loop_1 = loop_1.threePointArc((-0.28127, 0.0442), (-0.94711, 0.03967))
loop_1 = loop_1.threePointArc((-0.98497, 0.0409), (-1.02061, 0.03961))
loop_1 = loop_1.lineTo(-1.03164, 0.03007)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_37_interval_0.stl')