import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.17964), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50081, -0.88533)
loop_1 = loop_1.lineTo(-0.49677, -0.89748)
loop_1 = loop_1.lineTo(-0.4779, -0.90804)
loop_1 = loop_1.lineTo(-0.45406, -0.90742)
loop_1 = loop_1.lineTo(-0.44307, -0.88041)
loop_1 = loop_1.lineTo(-0.44818, -0.85772)
loop_1 = loop_1.lineTo(-0.46675, -0.85018)
loop_1 = loop_1.lineTo(-0.49426, -0.85801)
loop_1 = loop_1.lineTo(-0.50277, -0.88067)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/sketch_20_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/sketch_20_interval_0.stl')