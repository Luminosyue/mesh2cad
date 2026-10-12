import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.60718, 0.0389, 0.1617), normal=(-0.999, 0.04467, -6e-05), xDir=(0.04467, 0.999, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16305, -0.23177)
loop_1 = loop_1.lineTo(-0.16814, -0.24389)
loop_1 = loop_1.lineTo(-0.1701, -0.25567)
loop_1 = loop_1.lineTo(-0.17865, -0.2698)
loop_1 = loop_1.lineTo(-0.18423, -0.2813)
loop_1 = loop_1.lineTo(-0.18743, -0.29569)
loop_1 = loop_1.lineTo(-0.19198, -0.30682)
loop_1 = loop_1.lineTo(-0.18325, -0.32739)
loop_1 = loop_1.threePointArc((-0.17643, -0.33701), (-0.17068, -0.34496))
loop_1 = loop_1.lineTo(-0.16405, -0.35787)
loop_1 = loop_1.lineTo(-0.16242, -0.37468)
loop_1 = loop_1.lineTo(-0.16217, -0.22524)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_5_interval_0.stl')