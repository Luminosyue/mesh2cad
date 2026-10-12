import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.74763), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.17272, 0.57603)
loop_1 = loop_1.lineTo(-0.13684, 0.55232)
loop_1 = loop_1.lineTo(-0.13504, 0.56992)
loop_1 = loop_1.lineTo(-0.13596, 0.58707)
loop_1 = loop_1.lineTo(-0.13889, 0.60274)
loop_1 = loop_1.lineTo(-0.14103, 0.62133)
loop_1 = loop_1.lineTo(-0.17269, 0.57608)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.46)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_44_interval_0.stl')