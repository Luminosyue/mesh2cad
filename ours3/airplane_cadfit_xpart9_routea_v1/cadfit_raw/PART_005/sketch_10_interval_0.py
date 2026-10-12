import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.96413, 0.0806)
loop_1 = loop_1.lineTo(-0.96326, 0.07001)
loop_1 = loop_1.lineTo(-0.94114, 0.04784)
loop_1 = loop_1.lineTo(-0.93062, 0.04584)
loop_1 = loop_1.lineTo(-0.90985, 0.04974)
loop_1 = loop_1.lineTo(-0.90563, 0.08505)
loop_1 = loop_1.lineTo(-0.93656, 0.09705)
loop_1 = loop_1.lineTo(-0.95422, 0.09123)
loop_1 = loop_1.lineTo(-0.96413, 0.0806)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_005/sketch_10_interval_0.stl')