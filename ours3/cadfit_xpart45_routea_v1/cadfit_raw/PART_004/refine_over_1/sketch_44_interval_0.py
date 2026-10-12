import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, 0.23743), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24972, -0.29721)
loop_1 = loop_1.lineTo(-0.24961, -0.33545)
loop_1 = loop_1.lineTo(-0.1887, -0.33532)
loop_1 = loop_1.lineTo(-0.20673, -0.32776)
loop_1 = loop_1.lineTo(-0.24193, -0.30383)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.66)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_44_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_44_interval_0.stl')