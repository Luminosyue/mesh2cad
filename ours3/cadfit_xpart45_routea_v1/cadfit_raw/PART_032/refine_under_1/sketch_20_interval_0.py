import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.84303, 0.19772, -0.0896), normal=(0.99238, -0.12323, -0.00013), xDir=(-0.12323, -0.99238, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.28533, 0.1704)
loop_1 = loop_1.lineTo(-0.28804, 0.1704)
loop_1 = loop_1.lineTo(-0.28752, -0.1896)
loop_1 = loop_1.lineTo(0.28527, -0.1896)
loop_1 = loop_1.lineTo(0.28533, 0.16002)
loop_1 = loop_1.lineTo(0.28533, 0.1704)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.66)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_20_interval_0.stl')