import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.34885, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.22, 0.96106)
loop_1 = loop_1.lineTo(0.21984, 0.913)
loop_1 = loop_1.lineTo(0.2044, 0.92668)
loop_1 = loop_1.lineTo(0.19071, 0.93569)
loop_1 = loop_1.lineTo(0.16643, 0.95002)
loop_1 = loop_1.lineTo(0.14581, 0.96106)
loop_1 = loop_1.lineTo(0.21993, 0.96106)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.74)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_60_interval_0.stl')