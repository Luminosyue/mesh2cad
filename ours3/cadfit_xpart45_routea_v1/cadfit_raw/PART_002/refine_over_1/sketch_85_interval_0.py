import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.7708), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.14542, -0.54497)
loop_1 = loop_1.lineTo(-0.09282, -0.5689)
loop_1 = loop_1.lineTo(-0.14236, -0.54824)
loop_1 = loop_1.lineTo(-0.13121, -0.55887)
loop_1 = loop_1.lineTo(-0.09488, -0.58587)
loop_1 = loop_1.lineTo(-0.07077, -0.5903)
loop_1 = loop_1.lineTo(-0.05822, -0.59757)
loop_1 = loop_1.lineTo(-0.03501, -0.60574)
loop_1 = loop_1.lineTo(-0.22, -0.60532)
loop_1 = loop_1.lineTo(-0.21961, -0.51142)
loop_1 = loop_1.lineTo(-0.1462, -0.54462)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.38)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_85_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_85_interval_0.stl')