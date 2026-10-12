import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.69417, 0.1548, -0.07296), normal=(1.0, -0.0, -0.0), xDir=(-0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56636, 0.18704)
loop_1 = loop_1.lineTo(-0.56603, -0.17296)
loop_1 = loop_1.lineTo(0.66313, -0.17296)
loop_1 = loop_1.lineTo(0.66301, 0.18704)
loop_1 = loop_1.lineTo(-0.55039, 0.18704)
loop_1 = loop_1.lineTo(-0.56636, 0.18704)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_4_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_4_interval_0.stl')