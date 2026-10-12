import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.30474, -0.19707, -0.19242), normal=(-0.03495, 0.73931, 0.67246), xDir=(0.99888, 0.04722, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.58635, 0.02428)
loop_1 = loop_1.lineTo(-0.59214, 0.00183)
loop_1 = loop_1.threePointArc((-0.59204, -0.00896), (-0.59148, -0.01584))
loop_1 = loop_1.lineTo(0.67109, -0.02505)
loop_1 = loop_1.lineTo(0.68117, -0.01561)
loop_1 = loop_1.lineTo(0.68054, 0.01489)
loop_1 = loop_1.lineTo(-0.5713, 0.02198)
loop_1 = loop_1.lineTo(-0.58635, 0.02428)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_35_interval_0.stl')