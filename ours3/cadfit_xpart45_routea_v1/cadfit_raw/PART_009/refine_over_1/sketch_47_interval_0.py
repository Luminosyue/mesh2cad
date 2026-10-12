import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.72114, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.16593, -0.52979)
loop_1 = loop_1.lineTo(0.13649, -0.55318)
loop_1 = loop_1.lineTo(0.69813, -0.5529)
loop_1 = loop_1.lineTo(0.68003, -0.52979)
loop_1 = loop_1.lineTo(0.16631, -0.52979)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.37)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_47_interval_0.stl')