import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.59, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.70634, -0.05997)
loop_1 = loop_1.lineTo(0.70532, -0.14492)
loop_1 = loop_1.lineTo(-0.75891, -0.14219)
loop_1 = loop_1.lineTo(-0.75759, -0.05902)
loop_1 = loop_1.lineTo(0.69851, -0.05894)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_48_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_48_interval_0.stl')