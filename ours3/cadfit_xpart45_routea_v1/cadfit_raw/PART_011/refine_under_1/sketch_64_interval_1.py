import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.21, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.73943, 0.20515)
loop_1 = loop_1.lineTo(-0.74015, -0.15408)
loop_1 = loop_1.threePointArc((-0.7422, -0.09068), (-0.74102, -0.0387))
loop_1 = loop_1.threePointArc((-0.74125, 0.00358), (-0.74213, 0.04394))
loop_1 = loop_1.threePointArc((-0.74264, 0.09379), (-0.74375, 0.14139))
loop_1 = loop_1.lineTo(-0.74383, 0.19143)
loop_1 = loop_1.threePointArc((-0.74174, 0.19817), (-0.73953, 0.20492))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_64_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_64_interval_1.stl')